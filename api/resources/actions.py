from flask import request
from flask_restful import Resource
import logging
from ..request_models import GetActionsRequest
from ..database.get_actions import get_actions_between_dates
from ..utils import are_dates_valid, store_actions_in_db
from ..utils import flatten_observation
from datetime import datetime
from ..services import global_env_manager_instance
from ..icp import icp_predictor_instance
import cloudpickle

logger = logging.getLogger(__name__)

class GetActions(Resource):
    ALLOWED_ACTIONS_INTERVALS = ["1d"]
    SUPPORTED_PAIRS = ["BTC-USD"]

    def post(self):
        try:
            logger.info("Received GetActions POST request")
            get_actions_request = GetActionsRequest(**request.get_json())
            logger.info(f"Request parameters: {get_actions_request}")

            if not self._validate_request(get_actions_request):
                logger.warning(f"Invalid request parameters: {get_actions_request}")
                return {"message": "Invalid request parameters"}, 400

            actions = self._get_or_generate_actions(get_actions_request)
            logger.info(f"Retrieved {len(actions)} actions")

            return {
                "actions": self._format_actions(actions),
                "start": get_actions_request.start,
                "end": get_actions_request.end,
            }, 200

        except Exception as e:
            logger.error(f"Error fetching actions: {str(e)}", exc_info=True)
            return {"message": str(e)}, 500

    def _validate_request(self, request):
        return (
            request.interval in self.ALLOWED_ACTIONS_INTERVALS
            and request.pair in self.SUPPORTED_PAIRS
        )

    def _get_or_generate_actions(self, request):
        logger.info(f"Getting actions between dates: {request.start} - {request.end}")
        actions = get_actions_between_dates(**request.model_dump())
        start_date = datetime.strptime(request.start, "%Y-%m-%d")
        end_date = datetime.strptime(request.end, "%Y-%m-%d")

        if len(actions) > 0:
            logger.info(f"Found {len(actions)} existing actions")
            last_action_date = max(action.timestamp for action in actions)
            first_action_date = min(action.timestamp for action in actions)
            logger.info(
                f"Actions date range: {first_action_date} - {last_action_date}"
            )
            
            if start_date < first_action_date:
                logger.info(f"Requested start date is before the first action date, setting start date to first action date")
                request.start = first_action_date.strftime("%Y-%m-%d")

            if end_date > last_action_date and end_date <= datetime.now():
                logger.info(
                    "Requested date range outside existing actions, generating new actions"
                )
                actions = self._generate_new_actions(request)
        elif are_dates_valid(request.start, request.end):
            logger.info("No existing actions found, generating new ones")
            actions = self._generate_new_actions(request)
        else:
            logger.warning("Requested date range is invalid")

        return actions

    def _generate_new_actions(self, request):
        logger.info(
            f"Generating new actions for {request.pair} with interval {request.interval}"
        )
        
        env_result = global_env_manager_instance.get_env(request.pair, request.interval)
      
        to_store = []

        if env_result:
            logger.info("Using existing environment")
            global_env_manager_instance.update_env_data(
                request.pair, request.interval
            )
            
            env_data, norm_env = global_env_manager_instance.get_env(
                request.pair, request.interval
            )

            is_done = False
            
            observation = norm_env.envs[0]._get_observation()    
            print(norm_env.envs[0].df.shape, norm_env.envs[0].current_step)
            
            while not is_done:
                action = icp_predictor_instance.predict(observation)
                observation, reward, done, info = norm_env.step([action])
                is_done = done[0]
                logger.info(
                    f"Step result - Action: {action}, Reward: {reward[0]}, Done: {is_done}"
                )
                
                norm_env.render()

                flattened_observation = flatten_observation(observation)
                date = info[0]["date"].to_pydatetime()
                to_store.append(
                    {
                        "action": action,
                        "reward": reward[0],
                        "observation": flattened_observation,
                        "timestamp": date,
                        "interval": request.interval,
                    }
                )
        else:
            logger.info("Creating new environment")
            env_data_serialized, observation = global_env_manager_instance.create_env(
                pair=request.pair,
                interval=request.interval,
                initial_balance=10000,
                start=request.start,
                end=request.end,
            )
            global_env_manager_instance.save_env(
                request.pair, request.interval, env_data_serialized
            )

            env_data, norm_env = global_env_manager_instance.get_env(
                request.pair, request.interval
            )
            
            observation = norm_env.reset()
            is_done = False
 
            while not is_done:
                action = icp_predictor_instance.predict(observation)
                observation, reward, done, info = norm_env.step([action])
                is_done = done[0]

                logger.info(
                    f"Step result - Action: {action}, Reward: {reward[0]}, Done: {is_done}"
                )
                
                norm_env.render()

                flattened_observation = flatten_observation(observation)
                date = info[0]["date"].to_pydatetime()
                
                to_store.append(
                    {
                        "action": action,
                        "reward": reward[0],
                        "observation": flattened_observation,
                        "timestamp": date,
                        "interval": request.interval,
                    }
                )
            
    
        logger.info(f"Storing {len(to_store)} new actions in database")
        store_actions_in_db(to_store, request.pair)
        
        env_data["vec_normalize"] = norm_env
        env_data["env"] = norm_env.venv
        env_data_serialized = cloudpickle.dumps(env_data)
        global_env_manager_instance.save_env(
            request.pair, request.interval, env_data_serialized
        )
        
        return get_actions_between_dates(**request.model_dump())

    def _format_actions(self, actions):
        return [
            {
                "action": action.action,
                "timestamp": action.timestamp.isoformat(),
                "reward": action.reward,
                "observation": action.observation,
                "interval": action.interval,
            }
            for action in actions
        ]
