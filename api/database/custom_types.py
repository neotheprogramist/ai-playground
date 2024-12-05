from sqlalchemy.types import TypeDecorator, FLOAT
import numpy as np


class NumpyFloat(TypeDecorator):
    """
    Custom SQLAlchemy type to handle numpy float32 and float64.
    """

    impl = FLOAT

    def process_bind_param(self, value, dialect):
        if isinstance(value, np.float32) or isinstance(value, np.float64):
            return float(value)
        return value

    def process_result_value(self, value, dialect):
        return value
