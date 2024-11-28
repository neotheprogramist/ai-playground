from datetime import datetime
from api.database_models import Action
from typing import List, Dict
from sqlalchemy import and_

def get_actions_between_dates(pair: str, start: str, end: str, interval: str) -> List[Dict]:
    if interval not in ["1d", "1h"]:
        raise ValueError("Invalid interval")
      
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    
    actions = Action.query.filter(
        and_(
            Action.pair == pair,
            Action.timestamp >= start_date,
            Action.timestamp <= end_date,
            Action.interval == interval
        )
    ).all()
    
    return actions