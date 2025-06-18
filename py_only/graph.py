


# ---------------- Plot learning curve (raw and smoothed) and display runtime ----------------

import pickle
import matplotlib.pyplot as plt
import numpy as np
from config import GRAPH_FILE


def main():
    # Load training metrics
    with open(GRAPH_FILE, 'rb') as f:
        data = pickle.load(f)

    rewards = data['rewards']  # List of total rewards per episode
    duration = data['duration']  # Total training time in seconds

    # Plot raw learning curve
    plt.figure()
    plt.plot(range(1, len(rewards) + 1), rewards, alpha=0.3, label='Raw')

    # Compute and plot smoothed curve using moving average
    window = 20  # window size for moving average
    if len(rewards) >= window:
        smooth = np.convolve(rewards, np.ones(window) / window, mode='valid')
        # The smoothed series corresponds to episodes [window .. len(rewards)]
        plt.plot(range(window, len(rewards) + 1), smooth, label=f'{window}-episode MA')

    # Annotate plot
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title(f'Learning Curve (Duration: {duration:.2f}s)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
