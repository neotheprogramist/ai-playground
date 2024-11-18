import gymnasium as gym
import numpy as np
from collections import deque
from gymnasium import spaces


class CryptoTradingEnv(gym.Env):
    def __init__(self, df, window_size=10, initial_balance=1000, render_mode="human", num_features=5):
        super(CryptoTradingEnv, self).__init__()

        self.df = df.reset_index(drop=True)
        self.window_size = window_size
        self.initial_balance = initial_balance
        self.current_step = 0
        self.render_mode = render_mode

        self.actions_history = self.df[["Close", "RSI"]].copy()
        self.actions_history["Action"] = 0

        self.trade_fee = 0.001

        self._last_reward = 0
        self._last_action = 0
        self._balance_pct_buy = 0.1
        self._avg_buy_price = 0
        self._avg_sell_price = 0

        self.balance = initial_balance
        self.crypto_held = 0
        self.net_worth = initial_balance

        self.action_space = spaces.Discrete(3)  # 0: Hold, 1: Buy, 2: Sell

        self.observation_space = spaces.Dict(
            {
                "prices": spaces.Box(
                    low=-np.inf,
                    high=np.inf,
                    shape=(self.window_size, num_features),
                    dtype=np.float32,
                ),
                "portfolio": spaces.Box(
                    low=0, high=np.inf, shape=(3,), dtype=np.float32
                ),
            }
        )

        self.price_history = deque(maxlen=self.window_size)
        self._seed()

    def _seed(self, seed=None):
        np.random.seed(seed)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = self.window_size
        self.balance = self.initial_balance
        self.crypto_held = 0
        self.net_worth = self.initial_balance

        self.actions_history = self.df[["Close", "RSI"]].copy()
        self.actions_history["Action"] = 0

        self._last_reward = 0
        self._last_action = 0
        self._balance_pct_buy = 0.1
        self._avg_buy_price = 0
        self._avg_sell_price = 0

        self.price_history.clear()
        for i in range(self.current_step - self.window_size, self.current_step):
            self.price_history.append(self._get_price_features(i))

        return self._get_observation(), {}

    def _get_price_features(self, index):
        return self.df.loc[
            index, ["Close", "Volume", "RSI", "EMA_50", "Pct Change"]
        ].values.astype(np.float32)

    def _get_observation(self):
        obs = {
            "prices": np.array(self.price_history),
            "portfolio": np.array(
                [
                    self.balance,
                    self.crypto_held,
                    self.net_worth,
                ],
                dtype=np.float32,
            ),
        }
        return obs

    def _get_info(self):
        return dict(
            balance=self.balance,
            crypto_held=self.crypto_held,
            net_worth=self.net_worth,
            actions_history=self.actions_history,
        )

    def step(self, action):
        reward = self._take_action(action)
        self.actions_history.loc[self.current_step, "Action"] = action
        self.current_step += 1

        if self.current_step < len(self.df):
            self.price_history.append(self._get_price_features(self.current_step))
            done = False
            truncated = False
        else:
            done = True
            truncated = False

        self._last_reward = reward
        self._last_action = action

        if self.net_worth <= self.initial_balance * 0.5:
            done = True

        return self._get_observation(), reward, done, truncated, self._get_info()

    def _take_action(self, action):
        closest_last_peak = self._find_closest_last_peak_index(self.current_step)
        closest_next_peak = self._find_closest_next_peak_index(self.current_step)
        current_price = self.df.loc[self.current_step, "Close"]
        is_peak = self.df.loc[self.current_step, "Peak"]
        reward = 0.1

        if closest_next_peak is not None:
            peak_price = self.df.loc[closest_next_peak, "Close"]

            if action == 1:  # Buy
                balance_to_buy = self.balance * 1
                crypto_can_buy = balance_to_buy / current_price

                self.crypto_held += crypto_can_buy * (1 - self.trade_fee)
                self.balance -= crypto_can_buy * current_price

                reward = (peak_price - current_price) / 1000

            elif action == 2:  # Sell
                if (
                    closest_next_peak + 10 < self.current_step
                    and closest_next_peak - 10 > self.current_step
                ):
                    self.balance += (self.crypto_held * current_price) * (
                        1 - self.trade_fee
                    )
                    self.crypto_held = self.crypto_held - self.crypto_held

                    reward = 1000

        self.net_worth = self.balance + self.crypto_held * current_price

        return reward

    def _find_closest_next_peak_index(self, current_index, peak_col="Peak"):
        peak_indices = self.df.index[self.df[peak_col] == 1].to_list()
        greater_peaks = [i for i in peak_indices if i > current_index]

        if not greater_peaks:
            return None

        return min(greater_peaks)

    def _find_closest_last_peak_index(self, current_index, peak_col="Peak"):
        peak_indices = self.df.index[self.df[peak_col] == 1].to_list()
        lesser_peaks = [i for i in peak_indices if i < current_index]

        if not lesser_peaks:
            return None

        return max(lesser_peaks)

    def render(self, mode="human"):
        print(
            f"Step: {self.current_step}, Net Worth: {self.net_worth}, Balance: {self.balance}, Crypto Held: {self.crypto_held}, Last Reward: {self._last_reward}, Last Action: {self._last_action}, Avg Buy Price: {self._avg_buy_price}, Avg Sell Price: {self._avg_sell_price}"
        )
