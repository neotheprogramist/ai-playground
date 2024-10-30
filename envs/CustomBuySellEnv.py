import numpy as np
import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces

class CustomBuySellEnv(gym.Env):
    def __init__(
        self,
        data,
        initial_budget=10000,
        budget_threshold=0.1,
        investment_fraction=0.1,
        tx_fee=0.01,
    ):
        super(CustomBuySellEnv, self).__init__()

        self.data = data
        self.actions_data = pd.DataFrame({"Action": [0] * len(self.data)})

        self.budget_threshold = budget_threshold
        self.initial_budget = initial_budget
        self.budget_remaining = self.initial_budget
        self.budget = self.initial_budget
        self.investment_fraction = investment_fraction
        self.tx_fee = tx_fee

        self.done_idx = len(self.data) - 1
        self.current_step = 0
        self.invested = 0
        self.previous_action = 0  # 0 = HOLD
        self.capital_history = []

        self.action_space = spaces.Discrete(3, start=-1)  # Hold, Buy, Sell
        self.observation_space = spaces.Box(
            low=-np.inf, high=+np.inf, shape=(11,), dtype=np.float32
        )

    def check_done(self):
        if self.current_step >= self.done_idx or self.budget_remaining <= 0:
            return True

        return False

    def _calculate_reward(self, action):
        penalty = 0
        investment = self.budget_remaining * self.investment_fraction

        if action == 1:
            if self.budget_remaining > self.initial_budget * self.budget_threshold:
                self.budget_remaining -= investment
                self.invested += investment / self.current_price
            else:
                penalty += 0.5
        elif action == -1 and self.invested > 0:  # Sell action
            self.budget_remaining += (self.invested * self.current_price) * (
                1 - self.tx_fee
            )
            self.invested = 0
        elif action == 0:  # Hold action
            if self.previous_action == 0:  # Penalty for holding
                penalty += 0.1

        # update budget, cause it changes with the price
        self.budget = self.budget_remaining + self.invested * self.current_price

        reward = (
            100 * self.next_return * action
            - np.abs(action - self.previous_action) * self.tx_fee
        )

        if reward < 0:
            reward *= 1.5

        reward -= penalty

        return reward

    def _calculate_reward2(self, action):
        penalty = 0
        investment = self.budget_remaining * self.investment_fraction

        if action == 1:
            if self.budget_remaining > 0:
                self.budget_remaining -= investment
                self.invested += investment / self.current_price

                # penalty for buying after selling
                if self.previous_action == -1:
                    penalty += 0.1
            else:  # Penalty for buying if no budget
                penalty += 0.1
        elif action == -1:
            if self.invested > 0:
                self.budget_remaining += (self.invested * self.current_price) * (
                    1 - self.tx_fee
                )
                self.invested = 0

                # Penalty for selling imidiately after buying
                if self.previous_action == 1:
                    penalty += 0.1
                # Reward for selling after holding
                elif self.previous_action == 0:
                    penalty -= 0.1
            else:
                penalty += 0.2  # Penalty for selling if no investment
        elif action == 0:  # hold action
            if self.invested > 0:
                penalty -= 0.1
            else:
                penalty += 0.1

        # penalty for changing action
        penalty += np.abs(action - self.previous_action) * self.tx_fee

        # update budget, cause it changes with the price
        self.budget = self.budget_remaining + self.invested * self.current_price

        # reward for holding
        reward = 10 * self.next_return * action

        # additional penalty for negative rewards
        if reward < 0:
            reward *= 1.1

        reward -= penalty

        return reward

    def _get_observation(self):
        state = self.data[self.current_step][
            1:
        ]  # exclude next_day_reward from state (it's more like a target)
        state = self.data.scaler.transform(state.reshape(1, -1))

        state = np.concatenate(
            [
                state,
                [
                    [
                        self.budget / self.initial_budget,
                        self.budget_remaining / self.budget,
                        self.invested * self.current_price / self.initial_budget,
                    ]
                ],
            ],
            axis=-1,
        )

        return state.reshape(-1).astype(np.float32)

    def close(self):
        return self.actions_data

    def _next_day_return(self):
        return self.data[self.current_step][0]

    def reset(self, seed=None, options=None):
        self.current_step = 0
        self.previous_action = 0
        self.invested = 0
        self.done = False
        self.budget_remaining = self.initial_budget
        self.budget = self.initial_budget
        self.capital_history = []
        self.current_price = self.data.frame.iloc[self.current_step, :]["Adj Close"]
        self.current_state = self._get_observation()
        self.next_return = self._next_day_return()

        return (
            self.current_state,
            {"portfolio_value": self.budget},
        )

    def step(self, action):
        self.current_price = self.data.frame.iloc[self.current_step, :]["Adj Close"]
        self.current_state = self._get_observation()
        self.next_return = self._next_day_return()
        self.current_reward = self._calculate_reward(action)

        self.actions_data.loc[self.current_step, "Action"] = action

        self.capital_history.append(self.budget)
        self.previous_action = action

        self.current_step += 1
        self.done = self.check_done()

        if self.done:
            capital_increase = self.capital_history[-1] / self.capital_history[0]
            self.current_reward += (capital_increase - 1) * 10

            if self.current_step < self.done_idx:
                if capital_increase < 0:
                    self.current_reward += -10 * (1 - self.current_step / self.done_idx)

        return (
            self.current_state,
            self.current_reward,
            self.done,
            False,
            {"portfolio_value": self.budget},
        )
