from ic.client import Client
from ic.identity import Identity
from ic.agent import Agent
from ic.candid import encode, Types
import numpy as np
from .config.icp_config import ICPConfig, ICPEnvironment

import os
class ICPredictor:
    def __init__(self, environment: ICPEnvironment = ICPEnvironment.LOCAL):
        self.environment = environment
        self.canister_id = ICPConfig.get_canister_id(environment)
        self.ic_url = ICPConfig.get_ic_url(environment)
        self.client = Client(url=self.ic_url)
        self.identity = Identity()
        self.agent = Agent(self.identity, self.client)

    def decode_action(self, response):
        """Decode action from IC canister response"""
        result_variant = response[0]["value"]
        
        if list(result_variant.keys())[0] != ICPConfig.KEYS.OK:
            raise ValueError("Invalid response")
        action_variant = ICPConfig.ACTION_DECODE_MAP[list(result_variant[ICPConfig.KEYS.OK].keys())[0]]
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


if os.environ.get("IC_ENVIRONMENT") == "mainnet":
    icp_predictor_instance = ICPredictor(ICPEnvironment.MAINNET)
else:
    icp_predictor_instance = ICPredictor(ICPEnvironment.LOCAL)
