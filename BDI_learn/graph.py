


import sys
import glob
import pickle
import matplotlib.pyplot as plt
import numpy as np
import os


def find_latest_metrics():
    """Find the most recently modified metrics_py4j_*.pkl file"""
    files = glob.glob('graph_*.pkl')
    if not files:
        raise FileNotFoundError('No graph_*.pkl files found in current directory')
    return max(files, key=os.path.getmtime)
    # If you want to select a file, use this return and comment out the previous one
    #return 'graph_FrozenLake_v1.pkl'

def main():
    # Determine metrics file
    if len(sys.argv) > 1:
        metrics_file = sys.argv[1]
    else:
        metrics_file = find_latest_metrics()
    print(f'Loading metrics from: {metrics_file}')

    # Load data
    with open(metrics_file, 'rb') as f:
        data = pickle.load(f)

    rewards = data.get('rewards', [])
    durations = data.get('durations', [])
    total_duration = data.get('total_duration', 0.0)

    if not rewards:
        print('No rewards data found.')
        return

    # Plot rewards and durations
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

    # Rewards subplot
    ax1.plot(range(1, len(rewards)+1), rewards, alpha=0.3, label='Raw Rewards')
    window = min(20, len(rewards))
    if len(rewards) >= window:
        smooth_rewards = np.convolve(rewards, np.ones(window)/window, mode='valid')
        ax1.plot(range(window, len(rewards)+1), smooth_rewards, label=f'{window}-episode MA')
    ax1.set_ylabel('Reward')
    ax1.legend()
    ax1.grid(True)

    # Durations subplot
    ax2.plot(range(1, len(durations)+1), durations, alpha=0.3, label='Raw Duration')
    if len(durations) >= window:
        smooth_durations = np.convolve(durations, np.ones(window)/window, mode='valid')
        ax2.plot(range(window, len(durations)+1), smooth_durations, label=f'{window}-episode MA')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Duration (s)')
    ax2.legend()
    ax2.grid(True)

    fig.suptitle(f'Jason-Py4j Learning Curve (Total time: {total_duration:.2f}s)')
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == '__main__':
    main()