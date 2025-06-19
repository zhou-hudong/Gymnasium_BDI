


# ---------------- Training/Evaluation Loop ----------------

import os
import time
import pickle
from config import *
from enviroment import *
from qtable import QTable
from agent import Agent


def train(env: Environment, agent: Agent):
    """Training mode: run multiple episodes and update Q-table, while recording each episode's rewards and time"""
    rewards = []
    durations = []
    start_time = time.time()  # Start timing

    for episode in range(1, NUM_EPISODES + 1):
        ep_start = time.time()
        state = env.reset()
        total_reward = 0

        for step in range(MAX_STEPS_PER_EPISODE):

            action = agent.select_action(state)
            next_state, reward, done = env.step(action)

            agent.learn(state, action, reward, next_state)
            state = next_state
            total_reward += reward

            if done:
                break

        agent.decay_epsilon()
        rewards.append(total_reward)
        ep_duration = time.time() - ep_start
        durations.append(ep_duration)

        # Save Q-table regularly
        if episode % 50 == 0:
            agent.qtable.save(QTABLE_FILE)
            print(f"Episode {episode}/{NUM_EPISODES}: reward={total_reward:.2f}, epsilon={agent.epsilon:.3f} (saved)")
        else:
            print(f"Episode {episode}/{NUM_EPISODES}: reward={total_reward:.2f}, epsilon={agent.epsilon:.3f}")

    # Save after training is completed
    agent.qtable.save(QTABLE_FILE)
    print("Training completed, Q-table saved.")

    # # Save graph: Contains the list of rewards for each episode and the total running time
    total_time = time.time() - start_time
    with open(GRAPH_FILE, 'wb') as f:
        pickle.dump({
            'rewards': rewards,
            'durations': durations,  # <<— 写入每集时长列表
            'total_time': total_time  # <<— 写入总训练时长
        }, f)
    print(f"Training completed in {total_time:.2f}s, metrics saved to {GRAPH_FILE}")



def evaluate(env: Environment, qtable: QTable):
    """Evaluation mode: After loading the Q-table, run a sample Episode in human mode"""
    state = env.reset()
    total_reward = 0

    while True:
        action = int(qtable.best_action(state))
        next_state, reward, done = env.step(action)
        total_reward += reward
        state = next_state
        if done:
            break

    print(f"Evaluation completed, total reward: {total_reward:.2f}")


def main():
    # Initialize the environment
    env = Environment(ENV_NAME, RENDER_MODE, MAX_STEPS_PER_EPISODE)

    # Initialize or load Q-table
    if os.path.exists(QTABLE_FILE):
        qtable = QTable.load(QTABLE_FILE)
        print(f"Loaded Q-table from {QTABLE_FILE}")
    else:
        qtable = QTable(env.num_states, env.num_actions)
        print("Initialized new Q-table")

    # Determine training or evaluation based on the LEARN flag
    if LEARN:
        agent = Agent(qtable)
        train(env, agent)
    else:
        # Evaluate only: run the learned policy in human mode
        if RENDER_MODE != "human":
            print("Warning: human mode recommended for evaluation to see renderings.")
        while True:
            evaluate(env, qtable)

if __name__ == '__main__':
    main()