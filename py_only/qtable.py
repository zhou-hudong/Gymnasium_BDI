

# ---------------- Q-table management: init, update, save, load ----------------

import pickle
import numpy as np

class QTable:
    def __init__(self, num_states: int, num_actions: int):
        # Using NumPy 2D arrays to store Q values
        self.table = np.zeros((num_states, num_actions))

    def get(self, state: int, action: int) -> float:
        return self.table[state, action]

    def update(self, state: int, action: int, value: float):
        # Update the Q value corresponding to the specified (state, action)
        self.table[state, action] = value

    def best_action(self, state: int) -> int:
        # Returns the index of the action with the highest Q value in the current Q-table under a given state
        return int(np.argmax(self.table[state]))

    def save(self, filename: str):
        # Persist Q-table to file
        with open(filename, 'wb') as f:
            pickle.dump(self.table, f)

    @classmethod
    def load(cls, filename: str):
        # Loading Q-table from file
        with open(filename, 'rb') as f:
            data = pickle.load(f)
        num_states, num_actions = data.shape
        obj = cls(num_states, num_actions)
        obj.table = data
        return obj