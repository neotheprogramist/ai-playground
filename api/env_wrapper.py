from stable_baselines3.common.vec_env import DummyVecEnv
from meta.peaks_env import CryptoTradingEnv
from stable_baselines3.common.vec_env.base_vec_env import VecEnvStepReturn
import numpy as np
from copy import deepcopy
from typing import Tuple


class PickleableEnvWrapper(DummyVecEnv):
    def __init__(self, env: CryptoTradingEnv):
        super().__init__([lambda: env])

    def step_wait(self) -> VecEnvStepReturn:
        """
        Wait for the step commands to be sent to the environments.
        Overrides the original step_wait to prevent automatic resets.
        """
        for env_idx in range(self.num_envs):
            # Perform a step in the environment
            obs, self.buf_rews[env_idx], terminated, truncated, self.buf_infos[env_idx] = self.envs[env_idx].step(
                self.actions[env_idx]
            )
            
            # Convert to SB3 VecEnv API
            self.buf_dones[env_idx] = terminated or truncated
            self.buf_infos[env_idx]["TimeLimit.truncated"] = truncated and not terminated

            if self.buf_dones[env_idx]:
                pass
            
            # Save the observation
            self._save_obs(env_idx, obs)
        
        return (
            self._obs_from_buf(),
            np.copy(self.buf_rews),
            np.copy(self.buf_dones),
            deepcopy(self.buf_infos)
        )

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
