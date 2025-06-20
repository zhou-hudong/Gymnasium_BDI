# Gymnasium_BDI
Python Gymnasium Q-Learning with BDI agent in Java.

This project integrates a **BDI (Belief–Desire–Intention) agent** written in Java with the **Python Gymnasium** simulation environment, using **Py4J** as a communication bridge. It demonstrates how a rule-based agent (defined in Jason/ASL) can learn optimal policies in discrete reinforcement learning tasks (e.g., FrozenLake-v1, CliffWalking-v0) through **Q-Learning**.

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
    - I recommend using **PyCharm**, as in my situation

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
    cd BDI_run
    
    # Start Jason MAS Console
    jason app1.mas2j
    # Waits for Python side to connect
    ```
  - Open PyCharm and Run drive_gym.py
    - Or with command `python drive_gym.py`
   
If you want to see the graph of the trained model, you can run the file `graph.py`.

## BDI_Configuration

Configuration is done in the ASL agent file (e.g., agent_learn.asl):

```java
/* 1. Configuration */
learning_rate(0.1).
discount_factor(0.2).
epsilon(1).
epsilon_decay(0.995).

name_game("FrozenLake-v1").
//name_game("CliffWalking-v0").

render_mode("ansi").

max_episode_steps(100).

episode_count(200).

file("prova_lake.pkl").
//file("prova_walk.pkl").
```

> **Nota:** Remember that Lake has a variable `is_slippery`. If it's set to true, then each action has a certain chance of becoming a random action.

**Observation**
- **FrozenLake** gives a reward of 1 only upon reaching the goal. All other events, including falling in holes, return 0.
- To accelerate learning, the goal reward was multiplied by 100.

## Project_Structure

**main folder：**
  - **BDI_run** -> folder containing the normal run agent process
  - **BDI_learn** -> folder to train the model
  - **py_only** -> folder with only python RL

**folder：**
  - **.gradle  .idea  build**  ->  these are 3 folders automatically generated by gradle and jason commands
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
  - **graph.py** -> to visualize graphs based on reward and time used per episode
  - **.pkl**  ->  Saved Q-tables
  - **graph_*.pkl** -> saved data used to draw the graph
  - **view_file**  ->  java file for Q-Table display of .pkl models
    - viewing procedure:
      - javac view_file.java
      - java view_file
    - Modify FILE_PATH to the appropriate model:
      ```java
        FILE_PATH = "prova_lake.pkl"
      ```

## Note

1. **Using Thread in BDI_learn Env.java**: A separate thread was added to manage the interaction between the BDI agent and the Gymnasium environment during the learning phase (e.g., in `ansi` mode). Without this thread, a `sleep` would be required to prevent communication blocking at high speed.
If the agent remains in the same state for multiple steps, the BDI system may assume that the `newState` has already been handled. As a result, it won't trigger the `newState` function again, nor will it send any updated value back.
This sleep can also be added in Java — the important part is to allow some reaction time.
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

3. **Retraining Strategy in BDI_learn**: If the number of episodes or steps configured is too low, retraining the model may often be necessary. For example, in FrozenLake, if you're unlucky, the agent might never reach the goal in the early episodes, and in the program, after each episode the value of ε-Greedy decreases — the lower the value, the less likely the agent will explore paths that could lead to the goal.

4. **Observation** : Once training is finished in the **BDI_learn** folder, copy the resulting **.pkl** file into the **BDI_run** folder. The BDI_learn setup uses threads and queues to achieve high-speed learning, so it cannot support the slower “human” render mode reliably.

5. **How to Use py_only Folder** :
   - To select which environment to train, edit the following settings in `config.py`:
      ```python
      ENV_NAME = "CliffWalking-v0"    # Gymnasium Environment Name
      #ENV_NAME = "FrozenLake-v1"
      RENDER_MODE = "ansi"            # Rendering mode: "human", "ansi", or "none"
      #RENDER_MODE = "human"

      # Training control
      LEARN = True
      #LEARN = False

      # Checkpoint file
      QTABLE_FILE = "walk.pkl"      # Q-table name Save/load file
      #QTABLE_FILE = "lake.pkl"
      ```
   - Once the game is selected, you only need to run `main.py` to complete the training. If you want to visualize the graph, just run `graph.py`.
