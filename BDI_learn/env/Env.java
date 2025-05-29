package app1.env;

import jason.asSyntax.ASSyntax;
import jason.asSyntax.Literal;
import jason.asSyntax.Structure;
import jason.environment.Environment;
import py4j.GatewayServer;
import py4j.GatewayServer.GatewayServerBuilder;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.InetAddress;
import java.util.concurrent.locks.ReentrantLock;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import java.util.concurrent.TimeUnit;

import java.io.*;
import java.util.*;



public class Env extends Environment {
    private static final Logger logger = Logger.getLogger(Env.class.getName());
    private GatewayServer server;
    private IPyEnv pyEnv;
    private final ReentrantLock lock = new ReentrantLock();
    private Map<String,Double> qtableMap = new HashMap<>();
    private final BlockingQueue<String> pendingPercepts = new LinkedBlockingQueue<>();
    private volatile boolean running = true;

    @Override
    public void init(String[] args) {
        super.init(args);
        try {
            // open Py4J loger
            //GatewayServer.turnLoggingOn();
            //Logger.getLogger("py4j").setLevel(Level.ALL);

            // start GatewayServer
            InetAddress addr = InetAddress.getByName("127.0.0.1");
            server = new GatewayServerBuilder(this)
                .javaPort(25333)                // Java port
                .callbackClient(25334, addr)    // Python call back port
                .build();
            server.start();
            logger.info("[Java] GatewayServer started on ports 25333/25334");

        } catch (Exception e) {
            logger.log(Level.SEVERE, "Failed to start GatewayServer", e);
        }

        // ---------- Start the heartbeat thread -----------
        Thread delivery = new Thread(() -> {
            int count = 0;
            while (running) {
                try {
                    System.out.println("Delivery start");
                    String lit = pendingPercepts.poll(100, TimeUnit.MILLISECONDS);
                    if (lit != null) {
                        // Receive a normal newState and immediately clear the timeout count
                        count = 0;
                        addPerceptFromString(lit);
                        System.out.println("Delivered added lit: " + lit);
                    } else {
                        // The count is incremented only if there is no newState.
                        count++;
                        System.out.println("No percept this tick, count=" + count);
                        if (count > 5) {
                            // If the threshold is exceeded, the execution environment is reset
                            count = 0;
                            int initState = pyEnv.reset();
                            String resetLit = String.format("newState(%d,0.0,false)[source(percept)]", initState);
                            pendingPercepts.put(resetLit);
                            System.out.println("Forced reset, delivered: " + resetLit);
                        }
                    }
                } catch (Throwable t) {
                    System.out.println("Delivery error");
                }
            }
            System.out.println("Delivery start");
        });
        delivery.start();
        // ----------------------------------------
    }


    @Override
    public boolean executeAction(String agName, jason.asSyntax.Structure action) {
        if (!action.getFunctor().equals("executeAction")) {
            return false;
        }

        lock.lock();
        try {
            String actionName = action.getTerm(0).toString().replaceAll("\"", "");
            switch (actionName) {
                case "new_table":{
                    int ns = pyEnv.get_Num_States();
                    int na = pyEnv.get_Num_Actions();
                    logger.info("[Java] Initializing Q-table: " + ns + "×" + na);
                    clearQtable();
                    for (int s = 0; s < ns; s++){
                        for (int a = 0; a < na; a++){
                            String percept = String.format("qtable(%d,%d,0.0)", s, a);
                            //System.out.printf("qtable(%d,%d,0.0)", s, a);
                            addPerceptFromString(percept);
                            addQtable(s,a,0.0);
                        }
                    }
                    break;
                }

                case "new_game":{
                    String game = action.getTerm(1).toString().replaceAll("\"", "");
                    String mode = action.getTerm(2).toString().replaceAll("\"", "");
                    String step = action.getTerm(3).toString().replaceAll("\"", "");
                    pyEnv.initialize(game, mode, step);
                    break;
                }

                case "reset_env":{
                    int initState = pyEnv.reset();
                    clearPercepts();
                    String percept = String.format("newState(%d,0.0,false)[source(percept)]", initState);
                    pendingPercepts.put(percept);
                    System.out.println("reset_env enqueued: " + percept);
                    //addPerceptFromString(percept);
                    //informAgsEnvironmentChanged();

                    break;
                }

                case "step_env":{
                    System.out.println("step_env started");

                    clearPercepts();

                    int act = Integer.parseInt(action.getTerm(1).toString());
                    Object[] res = pyEnv.step(act);
                    //System.out.println(res);
                    int st = (int) res[0];


                    System.out.println("res contents (state, reward, term):");
                    for (int i = 0; i < res.length; i++) {
                        System.out.println("  res[" + i + "] = " + res[i]);
                    }


                    double r = (double) res[1];

                    boolean d = (boolean) res[2];


                    // add newState percept
                    /*String percept = String.format("newState(%d,%.2f,%b)[source(percept)]", st, r, d);
                    addPerceptFromString(percept);*/

                    String lit = String.format("newState(%d,%.2f,%b)[source(percept)]", st, r, d);
                    logger.fine("enqueue percept: " + lit + "，队列大小=" + pendingPercepts.size());
                    pendingPercepts.put(lit);

                    System.out.println("step_env finished");
                    return true;

                }


                case "save_qtable": {
                    String fname = action.getTerm(1).toString().replace("\"", "");

                    // -------------------------
                    // 1) serialization qtableMap
                    // -------------------------
                    try (ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream(fname))) {
                        out.writeObject(qtableMap);
                        logger.info("Saved Q-table (" + qtableMap.size() + " entries) to " + fname);
                    } catch (Exception e) {
                        logger.log(Level.SEVERE, "Error saving Q-table", e);
                    }
                    return true;
                }

                case "load_qtable": {
                    String fname = action.getTerm(1).toString().replace("\"", "");

                    // -------------------------
                    // 1) clear qtable
                    // -------------------------
                    removePerceptsByUnif(ASSyntax.parseLiteral("qtable(_,_,_)"));
                    clearQtable();

                    // -------------------------
                    // 2) deserialization qtableMap
                    // -------------------------
                    try (ObjectInputStream in = new ObjectInputStream(new FileInputStream(fname))) {
                        @SuppressWarnings("unchecked")
                        Map<String,Double> loaded = (Map<String,Double>) in.readObject();
                        qtableMap.putAll(loaded);
                        logger.info("Loaded Q-table (" + loaded.size() + " entries) from " + fname);
                    } catch (Exception e) {
                        logger.log(Level.SEVERE, "Error loading Q-table", e);
                        return true;  // Restituisce comunque true per evitare di bloccare l'agente
                    }

                    // -------------------------
                    // 3) ripristinare i dati in qtableMap come Belief del Agent
                    // -------------------------
                    for (Map.Entry<String,Double> entry : qtableMap.entrySet()) {
                        String[] parts = entry.getKey().split(",");
                        String s = parts[0], a = parts[1];
                        double v = entry.getValue();
                        // formatazione come qtable(s,a,v)[source(self)]
                        String lit = String.format("qtable(%s,%s,%.6f)[source(self)]", s, a, v);
                        addPerceptFromString(lit);
                    }
                    return true;
                }


                case "update_learn_table": {
                    int s = Integer.parseInt(action.getTerm(1).toString());
                    int a = Integer.parseInt(action.getTerm(2).toString());
                    double q = Double.parseDouble(action.getTerm(3).toString());
                    addQtable(s, a, q);
                    return true;
                }

                case "stop_thread": {
                    // 终止 Delivery 线程循环
                    running = false;
                    System.out.println("[Java] Received stop_thread ➔ stopping Delivery thread");
                    return true;
                }


                default:{
                    logger.warning("Unknown action: " + actionName);
                }
            }


        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error in executeAction", e);
        } finally {
            lock.unlock();
        }

        return true;
    }

    @Override
    public void stop() {
        running = false;
        super.stop();
        if (server != null) {
            server.shutdown();
            logger.info("GatewayServer closed");
        }
    }

    /**
     * Callback dell'ambiente di registrazione lato Python
     */
    public void registerPythonEnv(IPyEnv pyEnvImpl) {
        this.pyEnv = pyEnvImpl;
        logger.info("Ambiente Python registrato");

        addPerceptFromString("start");
        informAgsEnvironmentChanged();
    }


    /*
     Metodo Bridge: riceve una stringa, la analizza in un letterale e aggiunge
    */
    public void addPerceptFromString(String literal) {
        System.out.println("add start");
        try {
            Literal p = ASSyntax.parseLiteral(literal);
            addPercept(p);
            informAgsEnvironmentChanged();
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Impossibile analizzare o aggiungere consapevolezza: " + literal, e);
        }
        System.out.println("add finished");
    }

    private void addQtable(int s, int a, double v) throws Exception {
        qtableMap.put(s + "," + a, v);
    }

    private void clearQtable() {
        qtableMap.clear();
    }

}
