from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.candid import encode, Types
import numpy as np


CANISTER_ID = "bkyz2-fmaaa-aaaaa-qaaaq-cai"
IC_URL = "http://127.0.0.1:4943"
OK_KEY = "_17724"
HOLD_KEY = "_803992927"
BUY_KEY = "_3308326"
SELL_KEY = "_925480882"

DECODE_DICT = {HOLD_KEY: 0, BUY_KEY: 1, SELL_KEY: 2}


class ICPredictor:
    def __init__(self, canister_id=CANISTER_ID, ic_url=IC_URL):
        self.canister_id = canister_id
        self.ic_url = ic_url
        self.client = Client(url=self.ic_url)
        self.identity = Identity()
        self.agent = Agent(self.identity, self.client)

    def decode_action(self, response):
        """Decode action from IC canister response"""
        result_variant = response[0]["value"]
        
        
        if list(result_variant.keys())[0] != OK_KEY:
            raise ValueError("Invalid response")
        action_variant = DECODE_DICT[list(result_variant[OK_KEY].keys())[0]]
        return action_variant

    def predict(self, obs) -> int:
        """Get prediction from IC canister"""

        prices = obs["prices"].astype(np.float32).flatten().tolist()
        portfolio = obs["portfolio"].astype(np.float32).flatten().tolist()

        params = [
            {"type": Types.Vec(Types.Float32), "value": prices},
            {"type": Types.Vec(Types.Float32), "value": portfolio},
        ]

        response = self.agent.update_raw(self.canister_id, "get_action", encode(params))
        return self.decode_action(response)


icp_predictor_instance = ICPredictor()