import asyncio
from pathlib import Path
from typing import Optional, Tuple
from playwright.async_api import Page, Error as PlaywrightError
try:
    from ..models.schemas import PlannedAction, ActionType
except ImportError:
    from models.schemas import PlannedAction, ActionType


class ActionExecutor:
    def __init__(self, screenshot_dir: Path):
        self.screenshot_dir = screenshot_dir
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    async def execute_action(
        self, 
        page: Page, 
        action: PlannedAction,
        timeout_ms: int = 5000
    ) -> Tuple[str, Optional[Exception]]:
        """Execute a planned action and return result."""
        try:
            if action.type == ActionType.CLICK:
                selector = self._build_selector(action)
                if selector:
                    # Scroll into view first
                    await page.locator(selector).first.scroll_into_view_if_needed(
                        timeout=timeout_ms
                    )
                    await page.locator(selector).first.click(timeout=timeout_ms)
                    return "clicked", None
                return "selector_not_found", None
            
            elif action.type == ActionType.SCROLL:
                if action.target and action.target.selector:
                    # Scroll to specific element
                    await page.locator(action.target.selector).first.scroll_into_view_if_needed(
                        timeout=timeout_ms
                    )
                    return "scrolled_to_element", None
                else:
                    # General scroll
                    await page.evaluate("window.scrollBy(0, 300)")
                    return "scrolled", None
            
            elif action.type == ActionType.FILL:
                selector = self._build_selector(action)
                if selector and action.value:
                    await page.locator(selector).first.fill(action.value, timeout=timeout_ms)
                    return "filled", None
                return "selector_not_found", None
            
            elif action.type == ActionType.WAIT:
                wait_ms = action.ms or 1000
                await asyncio.sleep(wait_ms / 1000)
                return f"waited_{wait_ms}ms", None
            
            elif action.type == ActionType.NAV:
                if action.value:
                    await page.goto(action.value, wait_until="domcontentloaded")
                    return "navigated", None
                return "no_url_provided", None
            
            return "unknown_action", None
            
        except PlaywrightError as e:
            return "error", e
        except Exception as e:
            return "unexpected_error", e
    
    async def capture_screenshot(
        self,
        page: Page,
        run_id: str,
        agent_id: str,
        step: int,
        full_page: bool = False
    ) -> str:
        """Capture screenshot and return relative path."""
        filename = f"{agent_id}_step{step}.png"
        filepath = self.screenshot_dir / run_id / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        await page.screenshot(
            path=str(filepath),
            full_page=full_page
        )
        
        # Return the static URL path
        return f"/static/{run_id}/{filename}"
    
    def _build_selector(self, action: PlannedAction) -> Optional[str]:
        """Build selector from action target."""
        if not action.target:
            return None
        
        target = action.target
        
        # Try different selector strategies in order
        if target.text:
            # Use text selector
            return f"text={target.text}"
        
        if target.role and target.name:
            # Use role and name
            return f"{target.role}[name='{target.name}']"
        
        if target.selector:
            # Use direct selector
            return target.selector
        
        return None