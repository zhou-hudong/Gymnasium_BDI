


import random
import numpy as np
from qtable import QTable
from config import LEARNING_RATE, DISCOUNT_FACTOR, INITIAL_EPSILON, EPSILON_DECAY, MIN_EPSILON

class Agent:
    def __init__(self, qtable: QTable):
        self.qtable = qtable
        self.epsilon = INITIAL_EPSILON  # Initialize ε

    def select_action(self, state: int) -> int:
        """Use ε-greedy strategy, return action index"""
        if random.random() > self.epsilon:
            return self.qtable.best_action(state)
        else:
            return random.randrange(self.qtable.table.shape[1])

    def learn(self, state: int, action: int, reward: float, next_state: int):
        """
        Q-learning update formula:
        Q(s,a) ← Q(s,a) + α [r + γ max_a' Q(s',a') - Q(s,a)]
        """
        old_value = self.qtable.get(state, action)
        next_max = np.max(self.qtable.table[next_state])
        new_value = old_value + LEARNING_RATE * (reward + DISCOUNT_FACTOR * next_max - old_value)
        self.qtable.update(state, action, new_value)

    def decay_epsilon(self):
        """Decrease ε, stay above minimum value"""
        self.epsilon = max(self.epsilon * EPSILON_DECAY, MIN_EPSILON)