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

import java.io.*;
import java.util.*;



public class Env extends Environment {
    private static final Logger logger = Logger.getLogger(Env.class.getName());
    private GatewayServer server;
    private IPyEnv pyEnv;
    private final ReentrantLock lock = new ReentrantLock();
    private Map<String,Double> qtableMap = new HashMap<>();


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
                    addPerceptFromString(percept);

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
                    String percept = String.format("newState(%d,%.2f,%b)[source(percept)]", st, r, d);
                    addPerceptFromString(percept);


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
                        return true;  // It still returns true to avoid blocking the agent
                    }

                    // -------------------------
                    // 3) restore data in qtableMap as Agent's Belief
                    // -------------------------
                    for (Map.Entry<String,Double> entry : qtableMap.entrySet()) {
                        String[] parts = entry.getKey().split(",");
                        String s = parts[0], a = parts[1];
                        double v = entry.getValue();
                        // formatting as qtable(s,a,v)[source(self)]
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
        super.stop();
        if (server != null) {
            server.shutdown();
            logger.info("GatewayServer closed");
        }
    }

    /**
     * Python side logging environment callback
     */
    public void registerPythonEnv(IPyEnv pyEnvImpl) {
        this.pyEnv = pyEnvImpl;
        logger.info("Ambiente Python registrato");

        addPerceptFromString("start");
    }


    /*
     Bridge Method: Receives a string, parses it into a literal and adds
    */
    public void addPerceptFromString(String literal) {
        System.out.println("add Percept start");
        try {
            Literal p = ASSyntax.parseLiteral(literal);
            addPercept(p);
            informAgsEnvironmentChanged();
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Impossibile analizzare o aggiungere consapevolezza: " + literal, e);
        }
        System.out.println("add Percept finished");
    }

    private void addQtable(int s, int a, double v) throws Exception {
        qtableMap.put(s + "," + a, v);
    }

    private void clearQtable() {
        qtableMap.clear();
    }
}