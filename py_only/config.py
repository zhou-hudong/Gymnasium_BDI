


# ---------------- Configuration parameters for Q-learning ----------------

# Environment settings
ENV_NAME = "CliffWalking-v0"    # Gymnasium Environment Name
#ENV_NAME = "FrozenLake-v1"
#RENDER_MODE = "ansi"            # Rendering mode: "human", "ansi", or "none"
RENDER_MODE = "human"
MAX_STEPS_PER_EPISODE = 100       # Maximum number of steps per episode

# Training control
# Whether to train (True: learn Q-table; False: only evaluate, load existing Q-table)
#LEARN = True
LEARN = False
NUM_EPISODES = 200                # Total Episodes

# Learning parameters
LEARNING_RATE = 0.1               # α Learning rate
DISCOUNT_FACTOR = 0.2             # γ Discount factor
INITIAL_EPSILON = 1.0             # ε initial exploration rate
EPSILON_DECAY = 0.995             # ε Attenuation coefficient
MIN_EPSILON = 0.01                # ε minimum

# Reward shaping for FrozenLake
REWARD_SCALE = 100              # Reward amplification factor when reaching the goal

# Checkpoint file
QTABLE_FILE = "walk.pkl"      # Q-table name Save/load file
#QTABLE_FILE = "lake.pkl"