import redis
import threading
import cloudpickle
import uuid
from datetime import datetime, timedelta
from typing import Tuple
from utils.fetch_data_with_indicators import fetch_data_with_indicators, Api
from meta.peaks_env import CryptoTradingEnv
from stable_baselines3.common.vec_env import VecNormalize
from scipy.signal import find_peaks

from ..utils import flatten_observation
from ..env_wrapper import PickleableEnvWrapper

redis_client = redis.Redis(host="localhost", port=6380, db=0, decode_responses=False)
env_lock = threading.Lock()

class EnvManager:
    def __init__(self):
        self.redis = redis_client

    def _get_env_state_key(self, token: str) -> str:
        return f"env:{token}"

    def _validate_and_adjust_dates(
        self, start: str, end: str, interval: str
    ) -> Tuple[str, str]:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        current_date = datetime.now()

        lookback_period = 60
        if interval == "1d":
            start_adjusted = start_date - timedelta(days=lookback_period)
        elif interval == "1h":
            start_adjusted = start_date - timedelta(hours=lookback_period)
        elif interval == "1m":
            start_adjusted = start_date - timedelta(minutes=lookback_period)

        if end_date > current_date:
            end_date = current_date

        return start_adjusted.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    def create_env(
        self,
        initial_balance,
        start,
        end,
        interval,
        indicators,
        stock_symbol,
    ) -> dict:
        adjusted_start, adjusted_end = self._validate_and_adjust_dates(
            start, end, interval
        )

        data = fetch_data_with_indicators(
            api=Api.YAHOO,
            stock_symbol=stock_symbol,
            start=adjusted_start,
            end=adjusted_end,
            interval=interval,
            indicators=indicators,
        )
        data = data.copy()
        data["Pct Change"] = data["Close"].pct_change() * 100
        data.dropna(inplace=True)
        peaks, properties = find_peaks(
            data["Close"], height=100, prominence=5, distance=40
        )
        data["Peak"] = 0
        data.loc[data.index[peaks], "Peak"] = 1

        env_original = CryptoTradingEnv(data, initial_balance=initial_balance)
        env = PickleableEnvWrapper(env_original)
        norm_env = VecNormalize(env, norm_obs=True, norm_reward=False)
        observation = norm_env.reset()
        token = str(uuid.uuid4())
        observation = flatten_observation(observation)

        env_data = {
            "vec_normalize": norm_env,
            "env": env,
            "adjusted_start": adjusted_start,
            "adjusted_end": adjusted_end,
            "start": start,
            "end": end,
            "current": start,
            "stock_symbol": stock_symbol,
            "interval": interval,
            "indicators": indicators,
            "initial_balance": initial_balance,
        }

        env_data = cloudpickle.dumps(env_data)

        with env_lock:
            self.redis.set(self._get_env_state_key(token), env_data, ex=86400)

        return {
            "token": token,
            "observation": observation,
            "adjusted_start": adjusted_start,
            "adjusted_end": adjusted_end,
        }

    def _get_env_state(self, token: str) -> dict:
        env_state = self.redis.get(self._get_env_state_key(token))
        if not env_state:
            return None

        env_state = cloudpickle.loads(env_state)

        return env_state

    def get_env(self, token: str) -> VecNormalize:
        env_state = self._get_env_state(token)
        norm_env = env_state["vec_normalize"]
        env = env_state["env"]
        norm_env.set_venv(env)

        if not env_state:
            return None

        return norm_env

    def save_env(self, token: str, norm_env: VecNormalize):
        current_env_state = self._get_env_state(token)
        venv = norm_env.venv

        env_state = {
            **current_env_state,
            "vec_normalize": norm_env,
            "env": venv,
        }

        with env_lock:
            self.redis.set(
                self._get_env_state_key(token), cloudpickle.dumps(env_state), ex=86400
            )

    def delete_env(self, token: str):
        with env_lock:
            self.redis.delete(self._get_env_state_key(token))

    def update_env_data(self, token: str) -> str:
        env_state = self._get_env_state(token)

        if not env_state:
            return "invalid token"

        current_env = self.get_env(token)

        end = datetime.strptime(env_state["end"], "%Y-%m-%d")
        adjusted_end = datetime.strptime(env_state["adjusted_end"], "%Y-%m-%d")
        new_adjusted_end = datetime.now()

        if new_adjusted_end <= adjusted_end:
            return "no update needed"
        elif new_adjusted_end > end:
            new_adjusted_end = end

        new_end_str = new_adjusted_end.strftime("%Y-%m-%d")

        if new_end_str != env_state["adjusted_end"]:
            new_data = fetch_data_with_indicators(
                api=Api.YAHOO,
                stock_symbol=env_state["stock_symbol"],
                start=env_state["adjusted_start"],
                end=new_end_str,
                interval=env_state["interval"],
                indicators=env_state["indicators"],
            )

            new_data["Pct Change"] = new_data["Close"].pct_change() * 100
            new_data.dropna(inplace=True)
            peaks, _ = find_peaks(
                new_data["Close"], height=100, prominence=5, distance=40
            )
            new_data["Peak"] = 0
            new_data.loc[new_data.index[peaks], "Peak"] = 1

            current_env.df = new_data

            self.save_env(token, current_env)

            return "updated"

        return "no update needed"

