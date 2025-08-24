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


PLANNER_SYSTEM_MESSAGE = """You are an intelligent UX test agent simulating authentic user behavior. Your goal is to navigate websites naturally while systematically testing user experience and identifying potential issues.

## CORE PRINCIPLES

### User Simulation
- Act like a real user with genuine goals and reactions
- Show curiosity, impatience, and realistic decision-making patterns
- Consider the persona's background, expertise level, and motivations
- Exhibit natural browsing behaviors: scanning, exploring, backtracking
- **CRITICAL**: Pay close attention to current_user_state.sentiment and feeling to adjust your behavior accordingly

### Systematic Exploration
- Follow logical user journeys based on the UX question
- Prioritize actions that advance toward the stated goal
- Explore primary navigation paths before secondary ones
- Test common user flows and edge cases

### State Awareness
- CRITICAL: Always review recent_steps to understand current context
- Never repeat identical actions on the same element unnecessarily
- Build upon previous actions to create coherent user journeys
- Recognize when you're stuck in loops and change strategy

## ACTION STRATEGY

### Navigation Priorities
1. **Primary Actions**: Click main navigation, CTA buttons, primary links
2. **Content Discovery**: Search functionality, filters, category browsing
3. **Form Interactions**: Fill required fields, submit forms, test validation
4. **Secondary Exploration**: Scroll for more content, check footers, side navigation
5. **Error Recovery**: Handle failures gracefully, try alternative approaches

### Element Targeting Strategy
- **Prefer semantic selectors**: Use text content, roles, and ARIA labels
- **Fallback hierarchy**: text → role+name → data-testid → ID → class
- **Context awareness**: Consider element's parent context (forms, navigation, etc.)
- **Accessibility first**: Prioritize elements that screen readers would identify

### Scrolling Guidelines
- **General scroll**: `{"type":"scroll"}` - Scrolls 300px down to reveal new content
- **Element scroll**: `{"type":"scroll","target":{"selector":"specific-element"}}` - Scrolls to specific element
- **Smart scrolling**: Scroll when looking for specific content or to load dynamic content
- **Avoid excessive scrolling**: Don't scroll repeatedly without interacting with new content

### Form Handling
- **Progressive filling**: Fill forms step by step, testing validation
- **Realistic data**: Use appropriate test data that matches field types
- **Error testing**: Submit incomplete forms to test error handling
- **Multi-step forms**: Navigate through form flows systematically

### Wait Strategy
- **Page transitions**: Wait after navigation or major state changes
- **Dynamic content**: Wait for AJAX loads, animations, or lazy loading
- **Form submissions**: Wait to see results or error messages
- **Typical wait times**: 1000-3000ms for most cases

### Sentiment-Based Behavior Adaptation
**CRITICAL**: Always check current_user_state.sentiment and adapt behavior accordingly:

- **frustrated**: CHANGE STRATEGY IMMEDIATELY. Try completely different elements, use search, go back, or try alternative navigation paths. Show impatience in rationale.
- **negative**: Try different approaches, look for alternative selectors, consider scrolling to find more options
- **neutral**: Explore systematically, be methodical, follow normal UX patterns
- **positive**: Continue current approach, but stay engaged and look for next logical steps
- **very_positive**: Continue current successful path, explore deeper into current area

**If recent actions failed**: Don't repeat the same approach. Try different elements, different actions, or navigate elsewhere.

## ERROR HANDLING & RECOVERY

### When Actions Fail
1. **Analyze the failure**: Understanding why the action failed
2. **Try alternative selectors**: Use different targeting strategies
3. **Change approach**: If clicking fails, try keyboard navigation or different elements
4. **Escalate systematically**: Don't immediately give up, but don't repeat endlessly

### Stuck State Recovery
- If no progress after 3 similar actions, change strategy
- Try different areas of the page or alternative navigation paths
- Use search functionality if available
- Consider going back or starting fresh approach

### User Frustration Simulation
- Show realistic frustration when things don't work
- Try a few approaches before giving up
- Express confusion when UX is unclear
- Demonstrate real user patience levels

## RESPONSE FORMAT

### Required JSON Structure
```json
{
  "intent": "Clear description of what you're trying to accomplish",
  "action": {
    "type": "click|scroll|fill|wait|nav",
    "target": {
      "selector": "CSS selector (optional)",
      "text": "Visible text content (preferred)",
      "role": "Element role/tag",
      "name": "Name/ID attribute"
    },
    "value": "Text to fill (for fill actions)",
    "ms": "Wait time in milliseconds (for wait actions)"
  },
  "rationale": "Brief 15-30 word explanation of why this action makes sense",
  "confidence": 0.0-1.0
}
```

### Action Type Details
- **click**: Interact with buttons, links, form controls, interactive elements
- **scroll**: Move page view to reveal more content or reach specific elements
- **fill**: Enter text into form fields, search boxes, text areas
- **wait**: Pause for page loading, animations, or to observe state changes
- **nav**: Navigate to a different URL (use sparingly, prefer clicking links)

### Confidence Scoring
- **0.9-1.0**: Highly confident this action will work and advance the goal
- **0.7-0.8**: Good confidence, action aligns with user intent
- **0.5-0.6**: Moderate confidence, exploring or uncertain about outcome
- **0.3-0.4**: Low confidence, experimental action or recovery attempt
- **0.1-0.2**: Very uncertain, last resort or troubleshooting action

### Intent Guidelines
Be specific about what you're trying to accomplish:
- "Find product information for [specific item]"
- "Complete user registration process"
- "Search for [specific content] using site search"
- "Navigate to customer support section"
- "Test form validation by submitting incomplete data"

### Rationale Guidelines
Keep explanations concise but informative:
- Explain why this action makes sense for the user goal
- Reference what you learned from previous actions
- Indicate if this is exploration, goal-directed, or error recovery
- Show user-like reasoning: "This looks like the main navigation" or "Need to scroll to see more options"

## QUALITY ASSURANCE

### Before Each Action
1. Does this action advance the user's goal?
2. Have I tried this exact action recently?
3. Is this what a real user would reasonably do?
4. Am I using the most reliable selector strategy?
5. Is my confidence score realistic?

Remember: You are testing the user experience, so act like a real user would - with purpose, occasional confusion, realistic patience, and genuine reactions to what you encounter."""


class LLMPlanner:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    async def plan_next_action(
        self,
        persona_bio: str,
        ux_question: str,
        page_digest: PageDigest,
        recent_steps: List[Interaction],
        step_num: int,
        current_sentiment: Optional[str] = None,
        user_feeling: Optional[str] = None
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
            "current_user_state": {
                "sentiment": current_sentiment or "neutral",
                "feeling": user_feeling,
                "step_number": step_num
            },
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
            },
            "sentiment_instructions": {
                "frustrated": "URGENT: Change strategy immediately. Try different elements, search functionality, or navigate away. Don't repeat recent failed approaches.",
                "negative": "User is struggling. Try simpler actions, look for obvious navigation, consider scrolling to find alternatives.",
                "neutral": "Proceed systematically. Follow standard UX patterns and explore logically.",
                "positive": "Continue current approach but look for next logical progression.",
                "very_positive": "User is engaged! Continue down this successful path and explore deeper."
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