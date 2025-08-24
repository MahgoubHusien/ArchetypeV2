import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
try:
    from .models.schemas import (
        AgentInput, AgentOutput, Interaction, Session,
        DeviceType, FinishReason, ActionType, SentimentLevel, BugType
    )
    from .services.page_digest import extract_page_digest
    from .services.planner import LLMPlanner
    from .services.action_executor import ActionExecutor
    from .services.sentiment_analyzer import SentimentAnalyzer
except ImportError:
    from models.schemas import (
        AgentInput, AgentOutput, Interaction, Session,
        DeviceType, FinishReason, ActionType, SentimentLevel, BugType
    )
    from services.page_digest import extract_page_digest
    from services.planner import LLMPlanner
    from services.action_executor import ActionExecutor
    from services.sentiment_analyzer import SentimentAnalyzer


class UXAgent:
    def __init__(self, api_key: str, data_dir: Path = Path("data")):
        self.planner = LLMPlanner(api_key)
        self.executor = ActionExecutor(data_dir)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.data_dir = data_dir
        self.agent_id = f"agent_{uuid.uuid4().hex[:6]}"
    
    async def run(self, input_data: AgentInput) -> AgentOutput:
        """Run the agent through its planning loop."""
        interactions: List[Interaction] = []
        consecutive_errors = 0
        bugs_encountered = 0
        
        async with async_playwright() as p:
            # Launch browser with appropriate viewport
            browser = await self._launch_browser(p, input_data.viewport)
            context = await self._create_context(browser, input_data.viewport)
            page = await context.new_page()
            
            try:
                # Initial navigation
                await page.goto(input_data.url, wait_until="domcontentloaded")
                
                # Capture initial screenshot
                initial_screenshot = await self.executor.capture_screenshot(
                    page, input_data.run_id, self.agent_id, 0
                )
                
                # Main agent loop
                for step in range(1, input_data.step_budget + 1):
                    try:
                        # Extract page digest
                        page_digest = await extract_page_digest(page)
                        
                        # Analyze current sentiment BEFORE planning
                        current_sentiment, user_feeling = self.sentiment_analyzer.analyze_sentiment(
                            interactions, step, input_data.persona.bio
                        )
                        
                        # Plan next action with sentiment context
                        plan = await self.planner.plan_next_action(
                            persona_bio=input_data.persona.bio,
                            ux_question=input_data.ux_question,
                            page_digest=page_digest,
                            recent_steps=interactions,
                            step_num=step,
                            current_sentiment=current_sentiment,
                            user_feeling=user_feeling
                        )
                        
                        # Execute action
                        result, error = await self.executor.execute_action(
                            page, plan.action
                        )
                        
                        # Capture screenshot
                        screenshot = await self.executor.capture_screenshot(
                            page, input_data.run_id, self.agent_id, step
                        )
                        
                        # Detect bugs from action result
                        bug_detected, bug_type, bug_description = self.sentiment_analyzer.detect_bug(
                            result, {"url": page.url}
                        )
                        
                        if bug_detected:
                            bugs_encountered += 1
                        
                        # Generate dynamic thought based on current sentiment and bugs
                        dynamic_thought = self.sentiment_analyzer.generate_dynamic_thought(
                            current_sentiment, bug_detected, plan.action.type, plan.rationale
                        )
                        
                        # Log interaction
                        interaction = Interaction(
                            step=step,
                            intent=plan.intent,
                            action_type=plan.action.type,
                            selector=self._extract_selector(plan.action),
                            value=plan.action.value,
                            result=result,
                            thought=dynamic_thought,
                            ts=datetime.utcnow(),
                            screenshot=screenshot,
                            bug_detected=bug_detected,
                            bug_type=bug_type,
                            bug_description=bug_description,
                            sentiment=current_sentiment,
                            user_feeling=user_feeling
                        )
                        interactions.append(interaction)
                        
                        # Check for dropoff conditions
                        should_dropoff, dropoff_reason = self.sentiment_analyzer.check_dropoff_condition(
                            interactions, input_data.persona.bio, input_data.ux_question
                        )
                        
                        if should_dropoff:
                            finish_reason = FinishReason.USER_DROPOFF
                            break
                        
                        # Handle errors
                        if error:
                            consecutive_errors += 1
                            if consecutive_errors >= input_data.max_consecutive_errors:
                                finish_reason = FinishReason.CONSECUTIVE_ERRORS
                                break
                        else:
                            consecutive_errors = 0
                        
                        # Check for success conditions
                        if self._check_success(interactions, input_data.ux_question):
                            finish_reason = FinishReason.SUCCESS
                            break
                        
                    except Exception as e:
                        # Capture error screenshot
                        error_screenshot = await self.executor.capture_screenshot(
                            page, input_data.run_id, self.agent_id, step, full_page=True
                        )
                        
                        # Treat exceptions as bugs
                        bugs_encountered += 1
                        
                        # Analyze sentiment BEFORE logging the error
                        current_sentiment, user_feeling = self.sentiment_analyzer.analyze_sentiment(
                            interactions, step, input_data.persona.bio
                        )
                        
                        # Generate appropriate thought based on sentiment
                        if current_sentiment == SentimentLevel.FRUSTRATED:
                            error_thought = "This is really frustrating. The site keeps having technical issues."
                        elif current_sentiment == SentimentLevel.NEGATIVE:
                            error_thought = "Another error. This site is not working well."
                        else:
                            error_thought = "Encountered a technical issue. This is getting frustrating."
                        
                        interaction = Interaction(
                            step=step,
                            intent="Handling unexpected technical error",
                            action_type=ActionType.WAIT,
                            result=f"error: {str(e)}",
                            thought=error_thought,
                            ts=datetime.utcnow(),
                            screenshot=error_screenshot,
                            bug_detected=True,
                            bug_type=BugType.UNKNOWN,
                            bug_description=str(e),
                            sentiment=SentimentLevel.FRUSTRATED,  # Errors should always be frustrating
                            user_feeling="Frustrated by unexpected technical error"
                        )
                        interactions.append(interaction)
                        
                        consecutive_errors += 1
                        if consecutive_errors >= input_data.max_consecutive_errors:
                            finish_reason = FinishReason.CONSECUTIVE_ERRORS
                            break
                
                else:
                    # Loop completed without break
                    finish_reason = FinishReason.STEP_BUDGET_REACHED
                
            except Exception as e:
                finish_reason = FinishReason.NAV_FAILURE
            
            finally:
                await context.close()
                await browser.close()
        
        # Build output
        session = Session(
            url=input_data.url,
            device=DeviceType.MOBILE if input_data.viewport == "mobile" else DeviceType.DESKTOP,
            browser="chromium"
        )
        
        # Calculate overall sentiment
        if interactions:
            sentiment_values = [i.sentiment for i in interactions]
            sentiment_counts = {s: sentiment_values.count(s) for s in SentimentLevel}
            overall_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        else:
            overall_sentiment = SentimentLevel.NEUTRAL
            
        # Get dropoff reason if applicable
        dropoff_reason = None
        if finish_reason == FinishReason.USER_DROPOFF:
            _, dropoff_reason = self.sentiment_analyzer.check_dropoff_condition(
                interactions, input_data.persona.bio, input_data.ux_question
            )
        
        return AgentOutput(
            agent_id=self.agent_id,
            persona=input_data.persona,
            session=session,
            interactions=interactions,
            finish_reason=finish_reason,
            overall_sentiment=overall_sentiment,
            bugs_encountered=bugs_encountered,
            dropoff_reason=dropoff_reason
        )
    
    async def _launch_browser(self, playwright, viewport: str):
        """Launch browser with appropriate settings."""
        return await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
    
    async def _create_context(self, browser: Browser, viewport: str) -> BrowserContext:
        """Create browser context with viewport settings."""
        if viewport == "mobile":
            # iPhone 14 Pro viewport
            return await browser.new_context(
                viewport={"width": 393, "height": 852},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
            )
        else:
            # Desktop viewport
            return await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
    
    def _extract_selector(self, action) -> Optional[str]:
        """Extract selector string from action."""
        if action.target:
            if action.target.selector:
                return action.target.selector
            elif action.target.text:
                return f"text={action.target.text}"
            elif action.target.role and action.target.name:
                return f"{action.target.role}[name='{action.target.name}']"
        return None
    
    def _check_success(self, interactions: List[Interaction], ux_question: str) -> bool:
        """Check if we've successfully answered the UX question."""
        # For now, always return False to let the agent use its full step budget
        # The agent will stop when it reaches step_budget or encounters errors
        return False