# Gymnasium_BDI
Python Gymnasium Q-Learning with BDI agent in java

## Elenco

1. [Rapresentazione progetto](#Rapresentazione_progetto)
2. [Ambiente](#Ambiente)
3. [Run Project](#Run_Project)
4. [Code](#Code)
5. [Configurazione BDI](#Configurazione)
6. [Struttura del progetto](#Struttura_Project)
7. [Note](#Note)

## Rapresentazione_progetto

Il progetto **Gymnasium_BDI** integra un agente BDI (Belief–Desire–Intention) scritto in Java con l’ambiente di simulazione **Gymnasium** di Python, utilizzando **Py4J** come ponte di comunicazione. L’obiettivo è dimostrare come un agente basato su regole (definito in Jason/ASL) possa apprendere politiche ottimali in problemi di rinforzo discreti (ad es. FrozenLake-v1, Taxi-v3) tramite **Q-Learning**.

- **Architettura ibrida**  
  - **Java / Jason**: gestisce la logica BDI, la selezione delle azioni ε-greedy e la gestione delle Belief (Q-table).  
  - **Python / Gymnasium**: fornisce l’ambiente di simulazione (reset, step, render) e le sue dinamiche.  
  - **Py4J**: permette alle due parti di invocarsi a vicenda in modo sincrono e asincrono.

- **Workflow di un episodio**  
  1. **reset_env** (Java → Python) - *inizializzazione ambiente*
  2. Python restituisce 'newState(state, reward, done)'  
  3. L'agente BDI riceve 'newState(state, reward, done)', aggiorna Q-table (!learn) e seleziona la prossima azione (!selectAction)  
  4. **step_env(action)** invocato su Python - *manda prossimo azione all'ambiente*
  5. Nuovo `newState(...)`, ripetizione finché `done=true` (fine di un episodio)

- **Caratteristiche principali**  
  - Calcolo automatico di `num_states` e `num_actions` direttamente da Gymnasium  
  - Supporto a modalità di rendering `human` (grafico) e `ansi` (testuale - *per velocizzare learning*)  
  - Salvataggio e caricamento della Q-table (`.pkl`) per riprendere o analizzare le sessioni di apprendimento  
  - Configurabile via ASL - *senza modificare parte java e python*: learning rate, discount factor, ε-decay, numero di episodi, numero steps per episodio, ambiente di gioco

Questa soluzione consente di esplorare scenari di apprendimento per rinforzo mantenendo una chiara separazione tra **strategia BDI** e **dinamica ambientale**, facilitando estensioni a nuovi giochi Gymnasium con cambi minimi nella configurazione ASL.  

## Ambiente

Per eseguire correttamente il progetto, assicurati di avere installato e configurato i seguenti strumenti:

1. **Java 17+**  
   - Verifica la versione con  
     ```bash
     java -version
     ```
   - Se non lo hai, scaricalo dal sito ufficiale

2. **Jason (Jason Interpreter & IDE)**  
   - Jason è il motore BDI per ASL.  
   - Scaricalo dal repository ufficiale GitHub:  
     https://github.com/jason-lang/jason  
   - Segui le istruzioni in `README.md` del progetto per l’installazione e il lancio dell’interprete.
   - Nella cartella **examples** ci sono esempi di jason project
   - Se sei in Windows, scarica **git bash** per eseguire i comandi *jason* e *clone repository*

3. **Gradle**  
   - Usato per compilare e costruire la libreria Java–Py4J–Jason.  
   - Se installi Jason via GitHub, Gradle è già incluso nella cartella `tools/gradle`.  
   - Puoi anche installarlo globalmente seguendo le istruzioni:  
     https://gradle.org/install/

4. **Visual Studio Code** (o altro IDE a piacere)  
   - Estensioni consigliate:  
     - **Language Support for Java™ by Red Hat**  
     - **Gradle for Java**  
     - **Python**  
   - Imposta il workspace radice del repository per editing rapido di ASL, Java e Python.
   - Oppure puoi aprire la cartella invocando **code .** su **git bash**, che ti aprirà direttamente la cartella come workspace in **Visual Studio Code**

5. **Python 3.8+**  
   - Verifica con  
     ```bash
     python --version
     ```  
   - Crea un virtual environment (consigliato):  
     ```bash
     python -m venv .venv
     source .venv/bin/activate   # Linux/Mac
     .venv\Scripts\activate      # Windows
     ```
    - Se non voui eseguire con questi comandi, ti consiglio di usare **PyCharm**, come nella mia situazione

6. **Dipendenze Python**  
   - Installa Time, Gymnasium e Py4J:  
     ```bash
     pip install time gymnasium py4j
     ```  

7. **Configurazione porte Py4J**  
   - Di default:  
     - **JavaGateway** su porta `25333`  
     - **CallbackServer** su porta `25334`  
   - Assicurati che non siano in uso o modificane i valori in `drive_gym.py` e in `Env.java`.

## Run_Project

  - Apri **git bash** (caso Windows)
  - git clone https://github.com/zhou-hudong/Gymnasium_BDI
  - cd Gymnasium_BDI
  - jason app1.mas2j
    - aprirà la finestra MAS Console, per visualizzare Output e visualizzare Debug
    - All'inizio aspetterà il Run della parte Python
  - Open PyCharm an Run drive_gym.py
    - Java - Python si connette, e parte il programma

## Code

## Configurazione

Come possiamo vedere, ci sono 4 parti di configurazione:
  - Elementi per proseguire la formula di Q-Learning
  - Elementi di configurazione per Gymnasium
  - Max Steps
  - Max Episode
  - Nome del File di Q-Table dove salviamo e carichiamo

```java
/* 1. Configurazione */
learning_rate(0.1).
discount_factor(0.2).
epsilon(1).
epsilon_decay(0.995).

//name_game("FrozenLake-v1").
name_game("Taxi-v3").
//render_mode("human").
render_mode("ansi").

max_episode_steps(100).
//max_episode_steps(500).

episode_count(500).

file("prova_lake.pkl").
//file("prova_taxi.pkl").
```

> **Nota:** ricordati che Lake ha una dimensione piccolo, quindi Step = 100 è perfetto per allenare il modello, invece Taxi ha una dimensione grande, quindi ci servono uno Step alto, se no, non riuscirà a finire un intero episode raggiungendo l'obbiettivo

**Osservazione**
- **FrozenLake-v1** ha solo un reward = 1, qaundo raggiunge il goal, in altri casi, anche quando cade nel buco, il reward è sempre = 0
- **Taxi-v3** ogni passo ha sempre una sanzione di reward negativo, solo quando raggiunge il suo obbiettivo avrà reward positivo

## Struttura_Project

**Cartella：**
  - **.gradle  .idea  build**  ->  sono 3 cartelle create automaticamente dai comandi gradle e jason
  - **env** ->  cartella dove contiene il nostro Java Enviroment
    - **Env.java**  ->  Java Enviroment
    - **IPyEnv.java**  -> interfaccia Server Java-Python

**File**
  - **agent.asl**  ->  agente senza procedimento learn, carica modello ed esegue
  - **agent_learn.asl**  ->  agente con procedimento learn per allenare l modello
  - **app1.mas2j**  ->  file eseguibile per Jason
    - Per modificare Agent, devi cambiare il nome del file
      ```java
      MAS app1 {
        ...
        agents: agent_learn;
      }
      ```
  - **build.gradle **   settings.gradle  ->  file configurazione per gradle
  - **drive_gym.py**  ->  file eseguibile per Python
  - **.pkl**  ->  due file di modello allenato per i due ambienti Gymnasium
  - **view_file**  ->  file java per visualizzazione Q-Table degli modelli .pkl
    - procrdimento di visualizzazione:
      - javac view_file.java
      - java view_file
    - Per cambiare file .pkl da visualizzare, devi modificare il FILE_PATH:
      ```java
        FILE_PATH = "prova.pkl"
      ```

## Note

1. Puoi osservare che in modalità ansi, la velocità di learning non era molto veloce, era perchè ho aggiunto un spleep, per evitare che **py4j** si blocchi il taffico di comunicazione tra **java** e **python**
**Python**
```python
def step(self, action: int):
   ...
   time.sleep(0.2)
   ...
```

2. In Agent File, abbiamo una conversione di Source[Percept], da Percept a Self, questa conversione serve per evitare la cancellazione del Q-Table Belief del Agent da parte Java con "clearPercepts()"
   ```java
   +qtable(S,A,R)[source(percept)]<-
     +qtable(S,A,R)[source(self)];
     -qtable(S,A,R)[source(percept)].
   ```
