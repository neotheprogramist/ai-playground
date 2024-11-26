from stable_baselines3.common.vec_env import DummyVecEnv
from meta.peaks_env import CryptoTradingEnv


class PickleableEnvWrapper(DummyVecEnv):
    def __init__(self, env: CryptoTradingEnv):
        super().__init__([lambda: env])

    def __getstate__(self):
        state = self.__dict__.copy()

        state["envs"] = [env.__getstate__() for env in self.envs]
        state["env_fns"] = None

        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

        self.envs = []
        for env_state in state["envs"]:
            env = CryptoTradingEnv.__new__(CryptoTradingEnv)
            env.__setstate__(env_state)
            self.envs.append(env)
