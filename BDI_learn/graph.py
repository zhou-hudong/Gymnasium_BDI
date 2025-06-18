


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


def main():
    # Determine metrics file path
    if len(sys.argv) > 1:
        metrics_file = sys.argv[1]
    else:
        metrics_file = find_latest_metrics()
    print(f'Loading metrics from: {metrics_file}')

    # Load metrics data
    with open(metrics_file, 'rb') as f:
        data = pickle.load(f)

    rewards = data.get('rewards', [])
    duration = data.get('duration', 0.0)

    if not rewards:
        print('No rewards data found in metrics file.')
        return

    # Plot raw rewards per episode
    plt.figure()
    plt.plot(range(1, len(rewards) + 1), rewards, alpha=0.3, label='Raw')

    # Smooth curve via moving average
    window = min(20, len(rewards))
    if len(rewards) >= window:
        smooth = np.convolve(rewards, np.ones(window)/window, mode='valid')
        plt.plot(range(window, len(rewards) + 1), smooth, label=f'{window}-episode MA')

    # Formatting
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.title(f'Jason+Py4J Learning Curve (Duration: {duration:.2f}s)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()