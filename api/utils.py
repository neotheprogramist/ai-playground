import numpy as np
import logging
from datetime import datetime, timedelta
from .database_models import Action
from .db import db


MAX_ACTIONS_BEFORE_DATE = 200

def flatten_observation(
    observation_dict,
    target_shapes={
        "prices": (50,),
        "portfolio": (3,),
    },
):
    flattened_observation = {}
    for key, value in observation_dict.items():
        if isinstance(value, np.ndarray):
            try:
                flattened = value.reshape(target_shapes[key]).tolist()
                logging.info(
                    f"Reshaped '{key}' from {value.shape} to {target_shapes[key]}."
                )
            except ValueError as e:
                logging.error(f"Error reshaping '{key}': {e}. Flattening instead.")
                flattened = value.flatten().tolist()
            flattened_observation[key] = flattened
        else:
            flattened_observation[key] = value
    return flattened_observation


def are_dates_valid(start: str, end: str) -> bool:
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    print(start_date < end_date)
    print(datetime.now() - timedelta(days=MAX_ACTIONS_BEFORE_DATE))
    print(start_date >= datetime.now() - timedelta(days=MAX_ACTIONS_BEFORE_DATE))
    print(end_date <= datetime.now())
    return start_date < end_date and start_date >= datetime.now() - timedelta(days=MAX_ACTIONS_BEFORE_DATE) and end_date <= datetime.now()


def store_actions_in_db(actions, pair):
    for action in actions:
        action_record = Action(
            pair=pair,
            action=action['action'],
            reward=action['reward'],
            observation=action['observation'],
            interval=action['interval'],
            timestamp=action['timestamp']
        )
        db.session.add(action_record)
    db.session.commit()
