from datetime import datetime
from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field
from enum import Enum


class Viewport(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"


class ActionType(str, Enum):
    CLICK = "click"
    SCROLL = "scroll"
    FILL = "fill"
    WAIT = "wait"
    NAV = "nav"


class FinishReason(str, Enum):
    STEP_BUDGET_REACHED = "step_budget_reached"
    CONSECUTIVE_ERRORS = "consecutive_errors"
    NAV_FAILURE = "nav_failure"
    SUCCESS = "success"
    ERROR = "error"


class Persona(BaseModel):
    name: str
    bio: str


class AgentInput(BaseModel):
    run_id: str
    url: str
    persona: Persona
    ux_question: str
    viewport: Viewport = Viewport.MOBILE
    step_budget: int = 5
    max_consecutive_errors: int = 2
    seed: int = 7


class Session(BaseModel):
    url: str
    device: DeviceType
    browser: str = "chromium"


class Interaction(BaseModel):
    step: int
    intent: str
    action_type: ActionType
    selector: Optional[str] = None
    value: Optional[str] = None
    result: str
    thought: str
    ts: datetime
    screenshot: str


class AgentOutput(BaseModel):
    agent_id: str
    persona: Persona
    session: Session
    interactions: List[Interaction]
    finish_reason: FinishReason


class PageElement(BaseModel):
    role: Optional[str] = None
    name: Optional[str] = None
    text: Optional[str] = None
    label: Optional[str] = None
    placeholder: Optional[str] = None
    data_testid: Optional[str] = None
    selector_hint: Optional[str] = None
    visible: bool = True


class PageDigest(BaseModel):
    title: str
    url: str
    headings: List[str]
    interactives: List[PageElement]


class ActionTarget(BaseModel):
    selector: Optional[str] = None
    text: Optional[str] = None
    role: Optional[str] = None
    name: Optional[str] = None


class PlannedAction(BaseModel):
    type: ActionType
    target: Optional[ActionTarget] = None
    value: Optional[str] = None
    ms: Optional[int] = None


class PlanOutput(BaseModel):
    intent: str
    action: PlannedAction
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)