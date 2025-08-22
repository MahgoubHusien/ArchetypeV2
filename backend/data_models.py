from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class Agent(BaseModel):
    agent_id: UUID
    run_id: UUID
    persona: str 
    status: str
    started_at: datetime
    ended_at: datetime

class Interaction(BaseModel):
    interaction_id: UUID
    agent_id: UUID
    step: int
    intent: Optional[str] = None
    action_type: Optional[str] = None
    selector: Optional[str] = None # javascript selector for the element to interact with
    result: str  # result of the interaction
    created_at: datetime
    
    

class Run(BaseModel):
    run_id: UUID
    state: UUID
    url: str
    ux_question: Optional[str] = None
    created_at: datetime


