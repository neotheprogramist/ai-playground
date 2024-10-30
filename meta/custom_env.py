import gymnasium as gym
import numpy as np
from gymnasium import spaces

class CustomEnv(gym.Env):
    def __init__(self, data, action_space=3, observation_space=8, initial_balance=10000):
        super(CustomEnv, self).__init__()
        self.data = data.reset_index().copy()
        self.data['Action'] = 1
        self.actions_data = self.data.copy()

        self.action_space = spaces.Discrete(action_space)
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(observation_space,), dtype=np.float32)

        self._current_step = 0
        self._total_reward = 0.0

        self._pct_of_balance = 0.1

        self._initial_balance = initial_balance
        self._balance = initial_balance
        self._token_amount = 0
        self._balance_before_sell = 0
        self._last_action = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)
        self._current_step = 0
        self._total_reward = 0.0

        self._balance = self._initial_balance
        self._token_amount = 0
        self._balance_before_sell = 0
        self._last_action = None
        
        return (self._next_observation(), self._get_info())

    def _next_observation(self):
        obs = self.data.iloc[self._current_step][['Open', 'High', 'Low', 'Close', 'Volume']].values
        return obs.astype(np.float32)

    def step(self, action):
        current_price = self.data.iloc[self._current_step]['Close']
        if current_price <= 0:
            raise ValueError("Invalid current price encountered in data.")
        reward = 0

        self.actions_data.loc[self._current_step, 'Action'] = 1

        if action == 0:  # Buy
            if self._balance * self._pct_of_balance > 0:
                self._token_amount += self._balance * self._pct_of_balance / current_price
                self._balance -= self._balance * self._pct_of_balance
                reward = 0.01
                self.actions_data.loc[self._current_step, 'Action'] = action
            elif self._balance < 0:
                reward = -0.5
        elif action == 1:  # Hold
            reward = 0.1
        elif action == 2:  # Sell
            if self._token_amount > 0:
                self._balance_before_sell = self._balance
                self._balance += self._token_amount * current_price
                self._token_amount = 0
                self.actions_data.loc[self._current_step, 'Action'] = action
                reward = (self._balance - self._balance_before_sell) / 1000
            else:
                reward = -0.5


        self._current_step += 1
        done = self._current_step >= len(self.data) - 1
        obs = self._next_observation()
        self.current_reward = reward
        self._total_reward += reward
        self._last_action = action

        return obs, reward, done, False, self._get_info()

    def render(self, mode='human'):
        print(f'Step: {self._current_step}, Last Action: {self._last_action}, Reward: {self.current_reward}, Total Reward: {self._total_reward}, Balance Before: {self._balance_before_sell}, Balance: {self._balance}, Token Amount: {self._token_amount}')

    def close(self):
        return self.actions_data

    def _get_info(self):
        return dict(
            total_reward=self._total_reward,
            balance=self._balance,
            portfolio_value=self._balance + self._token_amount * self.data.iloc[self._current_step]['Close']
        )