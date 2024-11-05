import gymnasium as gym
import numpy as np
from gymnasium import spaces

class BuyAndHoldEnv(gym.Env):
    def __init__(self, data, action_space, observation_space, initial_balance=10000, transaction_cost=0.001):
        super(BuyAndHoldEnv, self).__init__()
        self.cached_data = data.copy()
        self.data = data.copy().reset_index()
        self.actions_data = data.copy().reset_index()
        self.actions_data['Action'] = 1

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
        self._transaction_cost = transaction_cost
        self._portfolio_value = initial_balance
        
        self._avg_buy_price = 0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)
        self._current_step = 0
        self._total_reward = 0.0
        self._current_reward = 0

        self._balance = self._initial_balance
        self._token_amount = 0
        self._balance_before_sell = 0
        self._last_action = None
        self._portfolio_value = self._initial_balance
        
        self.actions_data = self.cached_data.copy().reset_index()
        self.actions_data['Action'] = 1
        
        self._avg_buy_price = 0
        
        return (self._next_observation(), self._get_info())

    def _next_observation(self):
        stock_data = self.data.iloc[self._current_step][['Open', 'High', 'Low', 'Close', 'Volume', 'RSI']].copy()
        stock_data['Balance'] = self._balance
        stock_data['Token_Amount'] = self._token_amount
        stock_data['Portfolio_Value'] = self._portfolio_value
   
        return stock_data.values.astype(np.float32)

    def step(self, action):
        current_price = self.data.iloc[self._current_step]['Close']
        previous_price = self.data.iloc[self._current_step - 1]['Close']
        current_rsi = self.data.iloc[self._current_step]['RSI']
        
        if current_price <= 0:
            raise ValueError("Invalid current price encountered in data.")
        
        reward = 0

        if action == 0:  # Buy
            if self._balance > self._initial_balance * 0.05:
                self._token_amount += (self._balance * self._pct_of_balance / current_price) * (1 - self._transaction_cost)
                self._balance -= self._balance * self._pct_of_balance
                self.actions_data.loc[self._current_step, 'Action'] = action
                    
                if self._avg_buy_price == 0:
                    reward = 1
                else:
                    reward = (current_price - self._avg_buy_price)
                
                self._avg_buy_price = (self._avg_buy_price + current_price) / 2
            else:
                reward = -2
                
        elif action == 1:  # Hold
            if current_price > previous_price and self._token_amount > 0:
                reward = 1
            else:
                reward = -1

        self._current_step += 1
        done = self._current_step >= len(self.data) - 1
        self._portfolio_value = self._balance + self._token_amount * current_price
        obs = self._next_observation()
        
        self._current_reward = reward
        self._total_reward += reward
        self._last_action = action

        return obs, reward, done, False, self._get_info()
    
    def test_step(self, action):
        current_price = self.data.iloc[self._current_step]['Close']
        if current_price <= 0:
            raise ValueError("Invalid current price encountered in data.")

        self.actions_data.loc[self._current_step, 'Action'] = 1

        if action == 0:
            if self._balance > self._initial_balance * 0.05:
                self._token_amount += (self._balance * self._pct_of_balance / current_price) * (1 - self._transaction_cost)
                self._balance -= self._balance * self._pct_of_balance
                self.actions_data.loc[self._current_step, 'Action'] = action
                
        self._current_step += 1
        done = self._current_step >= len(self.data) - 1
        
        self._portfolio_value = self._balance + self._token_amount * current_price
        self._last_action = action
        
        return done, self._get_info()

    def render(self, mode='human'):
        print(f'Step: {self._current_step}, Last Action: {self._last_action}, Reward: {self._current_reward}, Total Reward: {self._total_reward}, Balance Before: {self._balance_before_sell}, Balance: {self._balance}, Token Amount: {self._token_amount}')

    def close(self):
        return self.actions_data

    def _get_info(self):
        return dict(
            total_reward=self._total_reward,
            balance=self._balance,
            portfolio_value=self._portfolio_value,
        )