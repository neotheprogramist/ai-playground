from flask import request
from flask_restful import Resource
import logging
from ..request_models import StepRequest, StepResponse
from ..services import env_manager_instance
from ..utils import flatten_observation

logger = logging.getLogger(__name__)


class StepEnv(Resource):
    def post(self):
        try:
            step_request = StepRequest(**request.get_json())
            token = request.headers.get("X-Session-Token")
            is_done = False

            if not token:
                return {"message": "Session token missing in headers."}, 400

            env_manager_instance.update_env_data(token)
            env = env_manager_instance.get_env(token)

            if env is None:
                return {"message": "Invalid or expired session token."}, 400

            if step_request.action not in [0, 1, 2]:
                return {
                    "message": "Invalid action. Must be 0 (Hold), 1 (Buy), or 2 (Sell)."
                }, 400

            observation, reward, done, info = env.step([step_request.action])
            observation = flatten_observation(observation)
            env_manager_instance.save_env(token, env)
            is_done = done[0]

            if is_done:
                env_manager_instance.delete_env(token)

            logger.info(
                f"Action {step_request.action} performed for token {token}. Reward: {reward}"
            )

            info = self._process_info(info[0])

            return (
                StepResponse(
                    observation=observation, done=is_done, info=info
                ).model_dump(),
                200,
            )
        except Exception as e:
            logger.error(f"Error stepping environment: {e}")
            return {"message": str(e)}, 500

    def _process_info(self, info):
        info_copy = dict()
        info_copy["actions_history"] = info["actions_history"].values.tolist()
        info_copy["balance"] = float(info["balance"])
        info_copy["crypto_held"] = float(info["crypto_held"])
        info_copy["net_worth"] = float(info["net_worth"])
        return info_copy
