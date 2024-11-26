from flask import Flask, request
from flask_restful import Resource, Api
from api.env_manager import EnvManager
from api.models import (
    StartRequest,
    StepRequest,
    ResetRequest,
    StartResponse,
    StepResponse,
)
from api.utils import flatten_observation
import logging
import numpy as np
from flask_cors import CORS


app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "X-Session-Token"],
    methods=["GET", "POST", "OPTIONS"],
)

api = Api(app)
env_manager = EnvManager()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StartSession(Resource):
    def post(self):
        try:
            start_request = StartRequest(**request.get_json())
            response = env_manager.create_env(
                initial_balance=start_request.initial_balance,
                start=start_request.start,
                end=start_request.end,
                interval=start_request.interval,
                indicators=["RSI", "EMA_50"],
                stock_symbol="BTC-USD",
            )
            logger.info(f"Session started with token: {response['token']}")
            return (
                StartResponse(
                    token=response["token"],
                    observation=response["observation"],
                    adjusted_start=response["adjusted_start"],
                    adjusted_end=response["adjusted_end"],
                ).model_dump(),
                201,
            )
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return {"message": str(e)}, 500


class StepEnv(Resource):
    def post(self):
        try:
            step_request = StepRequest(**request.get_json())
            token = request.headers.get("X-Session-Token")
            is_done = False

            if not token:
                return {"message": "Session token missing in headers."}, 400

            env_manager.update_env_data(token)
            env = env_manager.get_env(token)

            if env is None:
                return {"message": "Invalid or expired session token."}, 400

            if step_request.action not in [0, 1, 2]:
                return {
                    "message": "Invalid action. Must be 0 (Hold), 1 (Buy), or 2 (Sell)."
                }, 400

            observation, reward, done, info = env.step([step_request.action])
            observation = flatten_observation(observation)
            env_manager.save_env(token, env)
            is_done = done[0]

            if is_done:
                env_manager.delete_env(token)

            logger.info(
                f"Action {step_request.action} performed for token {token}. Reward: {reward}"
            )

            info = info[0]
            info_copy = info.copy()

            info_copy = dict()
            info_copy["actions_history"] = info["actions_history"].values.tolist()
            info_copy["balance"] = float(info["balance"])
            info_copy["crypto_held"] = float(info["crypto_held"])
            info_copy["net_worth"] = float(info["net_worth"])

            return (
                StepResponse(
                    observation=observation, done=is_done, info=info_copy
                ).model_dump(),
                200,
            )
        except Exception as e:
            logger.error(f"Error stepping environment: {e}")
            return {"message": str(e)}, 500


class ResetEnv(Resource):
    def post(self):
        try:
            reset_request = ResetRequest(**request.get_json())
            token = request.headers.get("X-Session-Token")
            if not token:
                return {"message": "Session token missing in headers."}, 400

            env = env_manager.get_env(token)
            if env is None:
                return {"message": "Invalid or expired session token."}, 400

            env_manager.delete_env(token)
            env_manager.create_env(
                initial_balance=reset_request.initial_balance,
                start=reset_request.start,
                end=reset_request.end,
                interval=reset_request.interval,
                indicators=["RSI", "EMA_50"],
                stock_symbol="BTC-USD",
            )

            return {
                "message": "Environment has been reset. Please start a new session with a new token."
            }, 200
        except Exception as e:
            logger.error(f"Error resetting environment: {e}")
            return {"message": str(e)}, 500


api.add_resource(StartSession, "/start")
api.add_resource(StepEnv, "/step")
api.add_resource(ResetEnv, "/reset")

if __name__ == "__main__":
    app.run(debug=True)
