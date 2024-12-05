from enum import Enum
from typing import NamedTuple
import os

class ICPEnvironment(Enum):
    LOCAL = "local"
    MAINNET = "mainnet"

class ICPKeys(NamedTuple):
    OK: str = "_17724"
    HOLD: str = "_803992927"
    BUY: str = "_3308326"
    SELL: str = "_925480882"

class ICPConfig:
    CANISTER_IDS = {
        ICPEnvironment.LOCAL: os.getenv('ICP_CANISTER_ID_LOCAL', 'bkyz2-fmaaa-aaaaa-qaaaq-cai'),
        ICPEnvironment.MAINNET: os.getenv('ICP_CANISTER_ID_MAINNET', '2bwko-gqaaa-aaaah-aq36q-cai')
    }
    
    IC_URLS = {
        ICPEnvironment.LOCAL: os.getenv('ICP_URL_LOCAL', 'http://127.0.0.1:4943'),
        ICPEnvironment.MAINNET: os.getenv('ICP_URL_MAINNET', 'https://a4gq6-oaaaa-aaaab-qaa4q-cai.raw.icp0.io/?id=2bwko-gqaaa-aaaah-aq36q-cai')
    }
    
    KEYS = ICPKeys()
    
    ACTION_DECODE_MAP = {
        KEYS.HOLD: 0,
        KEYS.BUY: 1,
        KEYS.SELL: 2
    }

    @classmethod
    def get_canister_id(cls, environment: ICPEnvironment) -> str:
        env_var = f"ICP_CANISTER_ID_{environment.value.upper()}"
        return os.getenv(env_var, cls.CANISTER_IDS[environment])

    @classmethod
    def get_ic_url(cls, environment: ICPEnvironment) -> str:
        env_var = f"ICP_URL_{environment.value.upper()}"
        return os.getenv(env_var, cls.IC_URLS[environment])
    