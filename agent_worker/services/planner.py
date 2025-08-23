import json
from typing import List, Optional
from openai import OpenAI
try:
    from ..models.schemas import (
        PageDigest, PlanOutput, PlannedAction, ActionTarget, 
        ActionType, Interaction, Persona
    )
except ImportError:
    from models.schemas import (
        PageDigest, PlanOutput, PlannedAction, ActionTarget, 
        ActionType, Interaction, Persona
    )


PLANNER_SYSTEM_MESSAGE = """You are a UX test agent simulating a real user. Emit one next action at a time in valid JSON only.

CRITICAL: Review recent_steps to see what you've already done. DO NOT repeat the same action on the same element.

Explore systematically:
1. Check recent_steps - if you clicked something, don't click it again
2. If scrolling failed, try a different scroll method or move to other actions
3. Look for new elements after each action
4. Try search/filter features if looking for specific content
5. Navigate to subpages if main page doesn't have what you need

For scrolling:
- Use general scroll: {"type":"scroll"} to scroll down 300px
- Or scroll to element: {"type":"scroll","target":{"selector":"h2"}}

Keep rationale ≤ 25 words.
Return exactly:
{"intent":"...","action":{"type":"click|scroll|fill|wait|nav","target":{"selector|text|role+name"},"value?":"","ms?":0},"rationale":"...","confidence":0.0}"""


class LLMPlanner:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    async def plan_next_action(
        self,
        persona_bio: str,
        ux_question: str,
        page_digest: PageDigest,
        recent_steps: List[Interaction],
        step_num: int
    ) -> PlanOutput:
        """Plan the next action based on current state."""
        
        # Format recent steps for context with full details
        recent_steps_data = []
        for step in recent_steps[-5:]:  # Last 5 steps for better context
            recent_steps_data.append({
                "step": step.step,
                "intent": step.intent,
                "action_type": step.action_type.value,
                "selector": step.selector,
                "result": step.result,
                "thought": step.thought
            })
        
        # Build planning input
        plan_input = {
            "persona_bio": persona_bio,
            "ux_question": ux_question,
            "page_digest": {
                "title": page_digest.title,
                "url": page_digest.url,
                "headings": page_digest.headings[:5],
                "interactives": [
                    {
                        "role": el.role,
                        "name": el.name,
                        "text": el.text[:50] if el.text else None,
                        "selector_hint": el.selector_hint
                    }
                    for el in page_digest.interactives
                ]
            },
            "recent_steps": recent_steps_data,
            "action_space": [
                {"type": "click", "fields": ["selector|text|role+name"]},
                {"type": "scroll", "fields": ["amount?", "to_selector?"]},
                {"type": "fill", "fields": ["selector", "value"]},
                {"type": "wait", "fields": ["ms"]},
                {"type": "nav", "fields": ["url"]}
            ],
            "constraints": {
                "return_format": "single_action_json",
                "max_words_rationale": 25,
                "forbidden": ["multi-step plans", "code"],
                "preferences": [
                    "prefer role/text/label over CSS",
                    "avoid repeating same action+selector 3x",
                    "choose action that most advances the UX goal"
                ]
            }
        }
        
        # Call LLM
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM_MESSAGE},
                {"role": "user", "content": json.dumps(plan_input, indent=2)}
            ],
            max_tokens=300,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        try:
            plan_data = json.loads(response.choices[0].message.content)
            
            # Convert to Pydantic model
            action_data = plan_data["action"]
            
            # Build target if present
            target = None
            if "target" in action_data:
                target_data = action_data["target"]
                target = ActionTarget(
                    selector=target_data.get("selector"),
                    text=target_data.get("text"),
                    role=target_data.get("role"),
                    name=target_data.get("name")
                )
            
            # Build planned action
            planned_action = PlannedAction(
                type=ActionType(action_data["type"]),
                target=target,
                value=action_data.get("value"),
                ms=action_data.get("ms")
            )
            
            return PlanOutput(
                intent=plan_data["intent"],
                action=planned_action,
                rationale=plan_data["rationale"],
                confidence=plan_data.get("confidence", 0.7)
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback action - wait and observe
            return PlanOutput(
                intent="Wait and observe page state",
                action=PlannedAction(
                    type=ActionType.WAIT,
                    ms=1000
                ),
                rationale="Failed to parse LLM response, waiting",
                confidence=0.1
            )