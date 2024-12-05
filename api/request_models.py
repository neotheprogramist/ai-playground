from pydantic import BaseModel
from typing import Dict, List

class StartRequest(BaseModel):
    initial_balance: float
    start: str
    end: str
    interval: str


class StartResponse(BaseModel):
    token: str
    observation: Dict
    adjusted_start: str
    adjusted_end: str


class ResetRequest(BaseModel):
    initial_balance: float
    start: str
    end: str
    interval: str


class StepRequest(BaseModel):
    action: int

class StepResponse(BaseModel):
    observation: Dict
    done: bool
    info: Dict
    
class GetActionsRequest(BaseModel):
    pair: str
    start: str
    end: str
    interval: str

class ActionWithTime(BaseModel):
    action: int
    time: str

class GetActionsResponse(BaseModel):
    actions: List[ActionWithTime]