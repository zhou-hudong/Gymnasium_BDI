from py4j.java_gateway import JavaGateway, GatewayParameters, CallbackServerParameters
import gymnasium as gym
import logging
import time

# Logger Configuration
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('py4j').setLevel(logging.DEBUG)

class PythonServer:
    class Java:
        implements = ["app1.env.IPyEnv"]

    def __init__(self):
        self.env = None
        self.render_mode = None
        self.Steps = 100
        self.reward_scale = 1000
        self.last_obs=0
        self.second_last_obs = None

    def initialize(self, env_name: str, render_mode: str, steps: str):
        """
        initialize environment, and save render_mode and Steps
        """
        self.render_mode = render_mode
        self.Steps = int(steps)
        if env_name == "FrozenLake-v1":
            self.env = gym.make(
                env_name,
                render_mode=render_mode,
                max_episode_steps=self.Steps,   # FrozenLake default 100 Step
                is_slippery = False  # ← to avoid the FrozenLake random action
            )
        else:
            self.env = gym.make(
                env_name,
                render_mode=render_mode,
                max_episode_steps=self.Steps,
            )
        print(f"[Python] Env initialized: {env_name}, mode: {render_mode}")

    def reset(self):
        """
        When the proxy requests a reset, it returns to its initial state
        """
        if self.env is None:
            raise RuntimeError("reset() called before initialize()")
        obs, _ = self.env.reset()
        # to print the "ansi" start text
        #if self.render_mode == "ansi":
        #    print(self.env.render(), end="")
        self.last_obs = obs
        self.second_last_obs = None
        return int(obs)

    def step(self, action: int):
        """
        In human mode, env.step will automatically render an ASCII map when you call step();
        In ANSI mode, you must manually get and print the string.
        """
        print("step start", action)
        obs, reward, term, trunc, _ = self.env.step(action)
        done = term or trunc

        # to signal the -1 reward for FrozenLake, when you fall into the hole
        if (term or trunc) and reward == 0:
            reward = -1.0
        # amplify the reward when it reaches the goal
        if done and reward > 0:
            reward = float(reward) * self.reward_scale
        else:
            reward = float(reward)
        # -5 when it always remains in the same state
        if not done and obs == self.last_obs:
            reward = float(reward) - 5.0
        # -2 when it rotates between two states
        if self.second_last_obs is not None and obs == self.second_last_obs:
            reward -= 2.0

        self.second_last_obs = self.last_obs
        self.last_obs = obs

        arr = self.gateway.new_array(self.gateway.jvm.Object, 3)
        arr[0], arr[1], arr[2] = obs, reward, done

        print("step call : ", obs, reward, done)
        return arr


    def get_Num_States(self):
        return int(self.env.observation_space.n)

    def get_Num_Actions(self):
        return int(self.env.action_space.n)


if __name__ == '__main__':
    server = PythonServer()

    cb_params = CallbackServerParameters(
        address='127.0.0.1',
        port=25334,
        daemonize=False,
        daemonize_connections=False,
        accept_timeout=0
    )
    gateway = JavaGateway(
        gateway_parameters=GatewayParameters(
            port=25333
        ),
        callback_server_parameters=cb_params,
        python_server_entry_point=server
    )
    server.gateway = gateway
    gateway.start_callback_server()
    print('[Python] Callback server listening on port', gateway.get_callback_server().get_listening_port())

    java_env = gateway.entry_point
    java_env.registerPythonEnv(server)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        gateway.shutdown()
        print('[Python] Connection closed')
