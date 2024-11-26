import numpy as np
import logging


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
