# Gymnasium_BDI
Python Gymnasium Q-Learning with BDI agent in Java.

This project integrates a **BDI (Belief–Desire–Intention) agent** written in Java with the **Python Gymnasium** simulation environment, using **Py4J** as a communication bridge. It demonstrates how a rule-based agent (defined in Jason/ASL) can learn optimal policies in discrete reinforcement learning tasks (e.g., FrozenLake-v1, Taxi-v3) through **Q-Learning**.

## Table of Contents

1. [Project Overview](#Project_Overview)
2. [Environment](#Environment)
3. [Run Project](#Run_Project)
4. [BDI Configuration](#BDI_Configuration)
5. [Project Structure](#Project_Structure)
6. [Notes](#Notes)

## Project_Overview

- **Hybrid Architecture**  
  - **Java / Jason**: Handles BDI logic, ε-greedy action selection, and Q-table belief management.  
  - **Python / Gymnasium**: Manages the environment (reset, step, render) and its dynamics. 
  - **Py4J**: Enables synchronous/asynchronous communication between Java and Python.

- **Episode Workflow**  
  1. **reset_env** (Java → Python): Initializes the environment.
  2. Python returns `newState(state, reward, done)`.  
  3. The BDI agent receives 'newState(state, reward, done)', updates the Q-table `(!learn)` e and selects the next action `(!selectAction)`.
  4. **step_env(action)** (Java → Python): Sends the next action to the environment.
  5. Repeats until `done = true` (end of episode).

- **Key Features**  
  - Automatic calculation of `num_states` and `num_actions` from Gymnasium.
  - Support for rendering modes: `human` (graphical) and `ansi` (text-based). 
  - Save/load Q-table as `.pkl` to resume or analyze learning sessions.
  - ASL-based configuration for: learning rate, discount factor, ε-decay, episodes, steps, and game environment.

This solution allows to explore reinforcement learning scenarios while maintaining a clear separation between **BDI strategy** and **environmental dynamics**, facilitating extensions to new Gymnasium games with minimal changes in the ASL configuration. 

## Environment

To run the project correctly, make sure you have the following tools installed and configured:

1. **Java 17+**  
   - Check the version with
     ```bash
     java -version
     ```
   - If you don't have it, download it from the official website

2. **Jason (Jason Interpreter & IDE)**  
   - Download it from the official GitHub repository:  
     https://github.com/jason-lang/jason  
   - Follow the instructions in the project's `README.md` to install and launch the interpreter.
   - In the **examples** folder there are examples of jason project
   - If you are on Windows, download **git bash** to run the *jason* and *clone repository* commands
   - Note: As you can see in the app1.mas2j file, the version the project uses is JASON 3.3.0

3. **Gradle**  
   - Included in tools/gradle when using Jason from GitHub. 
   - Or install globally: 
     https://gradle.org/install/

4. **Visual Studio Code** (or other IDE of your choice) 
   - Recommended Extensions: 
     - **Language Support for Java™ by Red Hat**  
     - **Gradle for Java**  
     - **Python**  
   - Set up the root workspace of the repository for fast editing of ASL, Java and Python.
   - Or Open project folder via `code .` in **Git Bash (Windows)**.

5. **Python 3.8+**  
   - Check with
     ```bash
     python --version
     ```  
   - Create a virtual environment (recommended): 
     ```bash
     python -m venv .venv
     source .venv/bin/activate   # Linux/Mac
     .venv\Scripts\activate      # Windows
     ```
    - I recommend you to use **PyCharm**, as in my situation

6. **Python Dependencies**  
   - Install Gymnasium and Py4J:  
     ```bash
     pip install gymnasium py4j
     ```  

7. **Py4J Port Configuration**  
   - Default:  
     - **JavaGateway** su porta `25333`  
     - **CallbackServer** su porta `25334`  
   - Modify in drive_gym.py and Env.java if needed.

## Run_Project

  - Open **git bash** (case Windows)
    ```python
    # Clone the project
    git clone https://github.com/zhou-hudong/Gymnasium_BDI.git
    cd Gymnasium_BDI
    
    # Start Jason MAS Console
    jason app1.mas2j
    # Waits for Python side to connect
    ```
  - Open PyCharm an Run drive_gym.py
    - Or with command `python drive_gym.py`

## BDI_Configuration

Configuration is done in the ASL agent file (e.g., agent_learn.asl):

```java
/* 1. Configurazione */
learning_rate(0.1).
discount_factor(0.2).
epsilon(1).
epsilon_decay(0.995).

name_game("FrozenLake-v1").
//name_game("CliffWalking-v0").

//render_mode("human").
render_mode("ansi").

//max_episode_steps(10).
max_episode_steps(100).

episode_count(200).

//file("prova_walk.pkl").
file("prova_lake.pkl").
//file("prova_taxi.pkl").
```

> **Nota:** ricordati che Lake ha una dimensione piccolo, quindi Step = 100 è perfetto per allenare il modello, invece Taxi ha una dimensione grande, quindi ci servono uno Step alto, se no, non riuscirà a finire un intero episode raggiungendo l'obbiettivo

**Observation**
- **FrozenLake** gives a reward of 1 only upon reaching the goal. All other events, including falling in holes, return 0.

## Struttura_Project

**folder：**
  - **.gradle  .idea  build**  ->  sono 3 cartelle create automaticamente dai comandi gradle e jason
  - **env** ->  folder where our Java Environment is contained
    - **Env.java**  ->  Java Enviroment
    - **IPyEnv.java**  -> Interface Server Java-Python

**File**
  - **agent.asl**  ->  Agent for inference only
  - **agent_learn.asl**  ->  Agent with learning logic
  - **app1.mas2j**  ->  MAS2J config file, executable file for Jason
    - To modify Agent, you need to change the file name
      ```java
      MAS app1 {
        ...
        agents: agent_learn;
        //agents: agent;
      }
      ```
  - **build.gradle   settings.gradle**  ->  Gradle config
  - **drive_gym.py**  ->  Python interface script
  - **.pkl**  ->  Saved Q-tables
  - **view_file**  ->  java file for Q-Table display of .pkl models
    - viewing procedure:
      - javac view_file.java
      - java view_file
    - Modify FILE_PATH to the appropriate model:
      ```java
        FILE_PATH = "prova_lake.pkl"
      ```

## Note

1. **Communication Delay**: You can see that in ansi mode, the learning speed was not very fast, it was because I added a sleep, To avoid communication blocking at high speed, if we remain in the same state over multiple steps, BDI considers the newState as already processed and therefore does not trigger the newState function or send a value back to Java.
This Sleep you can also add in JAVA, the important thing is to leave a reaction time
**Python**
```python
def step(self, action: int):
   ...
   time.sleep(0.2)
   ...
```

2. **Q-Table Belief Persistence**: In Agent File, we have a conversion of Source[Percept], from Percept to Self, this conversion is to avoid the deletion of the Agent's Q-Table Belief by Java with "clearPercepts()"
   ```java
   +qtable(S,A,R)[source(percept)]<-
     +qtable(S,A,R)[source(self)];
     -qtable(S,A,R)[source(percept)].
   ```

3. **Retraining Strategy**: Often you have to retrain the model, like in FrozenLake, if you are not lucky, it never reaches the goal in the first episodes, and in the program at each episode the value of ε-Greedy decreases, the lower the value, the less the agent focuses on discovering paths that could reach the goal.
