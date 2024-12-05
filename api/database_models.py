from .db import db
from .database.custom_types import NumpyFloat
from datetime import datetime

class Action(db.Model):
    __tablename__ = 'actions'
    
    id = db.Column(db.Integer, primary_key=True)
    pair = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, unique=True)
    action = db.Column(db.Integer, nullable=False)
    observation = db.Column(db.JSON, nullable=True)
    reward = db.Column(NumpyFloat, nullable=True)
    interval = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<Action {self.action} at {self.timestamp}>"

class GlobalEnvironment(db.Model):
    __tablename__ = 'global_environments'

    id = db.Column(db.Integer, primary_key=True)
    pair = db.Column(db.String, nullable=False)
    interval = db.Column(db.String, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

    __table_args__ = (db.UniqueConstraint('pair', 'interval', name='_pair_interval_uc'),)