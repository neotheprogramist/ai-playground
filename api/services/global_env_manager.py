from datetime import datetime, timedelta
from typing import Tuple, Dict
import cloudpickle
from ..utils import flatten_observation
from ..db import db
from ..database_models import GlobalEnvironment
from .env_manager import PickleableEnvWrapper
from scipy.signal import find_peaks
from stable_baselines3.common.vec_env import VecNormalize
from utils.fetch_data_with_indicators import fetch_data_with_indicators, Api
from meta.peaks_env import CryptoTradingEnv


class GlobalEnvManager:
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

    def _fetch_data(self, pair, interval, start, end):
        adjusted_start, adjusted_end = self._validate_and_adjust_dates(
            start, end, interval
        )
        data = fetch_data_with_indicators(
            api=Api.YAHOO,
            stock_symbol=pair,
            start=adjusted_start,
            end=adjusted_end,
            interval=interval,
            indicators=["RSI", "EMA_50"],
        )

        data = data.copy()
        data["Pct Change"] = data["Close"].pct_change() * 100
        data.dropna(inplace=True)
        peaks, _ = find_peaks(data["Close"], height=100, prominence=5, distance=40)
        data["Peak"] = 0
        data.loc[data.index[peaks], "Peak"] = 1
        return data, adjusted_start, adjusted_end

    def create_env(self, pair, interval, initial_balance, start, end):
        data, adjusted_start, adjusted_end = self._fetch_data(
            pair, interval, start, end
        )
        env_original = CryptoTradingEnv(data, initial_balance=initial_balance)
        env_pickleable = PickleableEnvWrapper(env_original)
        norm_env = VecNormalize(env_pickleable, norm_obs=True, norm_reward=False)
        observation = norm_env.reset()
        observation = flatten_observation(observation)

        env_data = {
            "vec_normalize": norm_env,
            "env": env_pickleable,
            "adjusted_start": adjusted_start,
            "adjusted_end": adjusted_end,
            "pair": pair,
            "interval": interval,
            "initial_balance": initial_balance,
            "indicators": ["RSI", "EMA_50"],
        }

        env_data_serialized = cloudpickle.dumps(env_data)
        return env_data_serialized, observation

    def save_env(self, pair, interval, env_data_serialized):
        try:
            env = GlobalEnvironment.query.filter_by(
                pair=pair, interval=interval
            ).first()
            if env:
                env.data = env_data_serialized
            else:
                env = GlobalEnvironment(
                    pair=pair, interval=interval, data=env_data_serialized
                )
                db.session.add(env)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def get_env(self, pair, interval) -> Tuple[Dict, VecNormalize]:
        env = GlobalEnvironment.query.filter_by(pair=pair, interval=interval).first()
        if env:
            env_data = cloudpickle.loads(env.data)
            norm_env = env_data["vec_normalize"]
            env = env_data["env"]
            norm_env.set_venv(env)
            return env_data, norm_env
        return None

    def delete_env(self, pair, interval):
        try:
            GlobalEnvironment.query.filter_by(pair=pair, interval=interval).delete()
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def update_env_data(self, pair, interval, new_end):
        env_data, norm_env = self.get_env(pair, interval)

        new_end = datetime.strptime(new_end, "%Y-%m-%d")
        adjusted_end = datetime.strptime(env_data["adjusted_end"], "%Y-%m-%d")
        now = datetime.now()

        if new_end <= adjusted_end:
            return
        elif new_end > adjusted_end and new_end <= now:
            adjusted_end = new_end
        else:
            adjusted_end = now

        new_data = fetch_data_with_indicators(
            api=Api.YAHOO,
            stock_symbol=env_data["pair"],
            start=env_data["adjusted_start"],
            end=adjusted_end.strftime("%Y-%m-%d"),
            interval=env_data["interval"],
            indicators=env_data["indicators"],
        )

        new_data = new_data.copy()
        new_data["Pct Change"] = new_data["Close"].pct_change() * 100
        new_data.dropna(inplace=True)
        peaks, _ = find_peaks(new_data["Close"], height=100, prominence=5, distance=40)
        new_data["Peak"] = 0
        new_data.loc[new_data.index[peaks], "Peak"] = 1

        env_data["env"].envs[0].refresh_data(new_data)
        env_data["adjusted_end"] = adjusted_end.strftime("%Y-%m-%d")
        self.save_env(
            env_data["pair"], env_data["interval"], cloudpickle.dumps(env_data)
        )
    
