


# Plot learning curve (raw and smoothed) and display runtime

import pickle
import matplotlib.pyplot as plt
import numpy as np
from config import GRAPH_FILE

def main():
    # Load training metrics from file
    with open(GRAPH_FILE, 'rb') as f:
        data = pickle.load(f)

    rewards = data.get('rewards', [])
    durations = data.get('durations', [])
    total_time = data.get('total_time', 0.0)

    # Create a figure with two subplots (2 rows, 1 column)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

    # Subplot 1: Learning curve for rewards
    ax1.plot(range(1, len(rewards) + 1), rewards, alpha=0.3, label='Raw Rewards')
    window = min(20, len(rewards))
    if len(rewards) >= window:
        # Calculate moving average for rewards
        smooth_rewards = np.convolve(rewards, np.ones(window)/window, mode='valid')
        ax1.plot(range(window, len(rewards) + 1), smooth_rewards, label=f'{window}-episode MA')
    ax1.set_ylabel('Reward')
    ax1.legend()
    ax1.grid(True)

    # Subplot 2: Episode durations and their smoothed curve
    ax2.plot(range(1, len(durations) + 1), durations, alpha=0.3, label='Raw Duration')
    if len(durations) >= window:
        # Calculate moving average for durations
        smooth_durations = np.convolve(durations, np.ones(window)/window, mode='valid')
        ax2.plot(range(window, len(durations) + 1), smooth_durations, label=f'{window}-episode MA')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Time (s)')
    ax2.legend()
    ax2.grid(True)

    # Overall title with total training time
    fig.suptitle(f'Python Only Learning Curve (Total time: {total_time:.2f}s)')
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == '__main__':
    main()

