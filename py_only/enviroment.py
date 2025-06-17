
# ---------------- Wrapper around Gymnasium environment ----------------

import gymnasium as gym
from config import REWARD_SCALE

class Environment:
    def __init__(self, name: str, render_mode: str, max_steps: int):
        """
        Initialize the Gymnasium environment
        :param name: environment name, such as "CliffWalking-v0"
        :param render_mode: "human", "ansi" or "none"
        :param max_steps: maximum number of steps per Episode
        """
        self.name = name
        # Open the visualization window only in human mode
        self.render_mode = render_mode if render_mode == "human" else None
        self.max_steps = max_steps
        if name == "FrozenLake-v1":
            self.env = gym.make(
                name,
                render_mode=render_mode,
                max_episode_steps=self.max_steps,   # FrozenLake default 100 Step
                is_slippery = False  # ← to avoid the FrozenLake random action
            )
        else:
            self.env = gym.make(
                name,
                render_mode=self.render_mode,
                max_episode_steps=self.max_steps,
            )
        # Used to detect continuous or cyclic status
        self.last_obs = None
        self.second_last_obs = None

    def reset(self) -> int:
        """Reset the environment and return to the initial state"""
        obs, _ = self.env.reset()
        self.last_obs = obs
        self.second_last_obs = None
        #if self.render_mode == "human":  # If in visualization mode, render once immediately
        #    self.env.render()
        return int(obs)

    def step(self, action: int):
        """
        Execute the action and return (next state, reward, whether it is finished)
        Also includes the following reward shaping strategies:
        1. Signal -1 when falling into the ice cave (FrozenLake)
        2. Reward *REWARD_SCALE when reaching the target
        3. If the state does not change, deduct -5
        4. If you go back and forth between two states, an additional deduction of -2
        """
        obs, reward, terminated, truncated, _ = self.env.step(action)
        done = terminated or truncated

        if self.name == "FrozenLake-v1":
            # Falling into an ice cave: When the environment ends and reward==0, reset to -1
            if done and reward == 0:
                reward = -1.0
            # Reaching the goal: positive reward amplification
            elif done and reward > 0:
                reward = float(reward) * REWARD_SCALE
            else:
                reward = float(reward)

        # Consecutive same state penalty
        if not done and obs == self.last_obs:
            reward -= 5.0
        # Penalty for switching between two states
        if self.second_last_obs is not None and obs == self.second_last_obs:
            reward -= 2.0

        # Update history status tracking
        self.second_last_obs = self.last_obs
        self.last_obs = obs

        #if self.render_mode == "human":
        #    self.env.render()
        return int(obs), float(reward), done

    @property
    def num_states(self) -> int:
        return self.env.observation_space.n

    @property
    def num_actions(self) -> int:
        return self.env.action_space.n