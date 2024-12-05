from flask import request
from flask_restful import Resource
import logging
from ..request_models import StartRequest, ResetRequest, StartResponse
from ..services import env_manager_instance

logger = logging.getLogger(__name__)

class StartSession(Resource):
    def post(self):
        try:
            start_request = StartRequest(**request.get_json())
            response = env_manager_instance.create_env(
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
          
class ResetEnv(Resource):
    def post(self):
        try:
            reset_request = ResetRequest(**request.get_json())
            token = request.headers.get("X-Session-Token")
            if not token:
                return {"message": "Session token missing in headers."}, 400

            env = env_manager_instance.get_env(token)
            if env is None:
                return {"message": "Invalid or expired session token."}, 400

            env_manager_instance.delete_env(token)
            env_manager_instance.create_env(
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

