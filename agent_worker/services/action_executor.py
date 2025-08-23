import asyncio
from pathlib import Path
from typing import List, Optional, Tuple
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
                    try:
                        # Scroll into view first
                        await page.locator(selector).first.scroll_into_view_if_needed(
                            timeout=timeout_ms
                        )
                        await page.locator(selector).first.click(timeout=timeout_ms)
                        return "clicked", None
                    except Exception as e:
                        # If primary selector fails, try building multiple selectors
                        target = action.target
                        if target:
                            fallback_selectors = []
                            if target.text:
                                clean_text = target.text.strip()
                                fallback_selectors.extend([
                                    f'text="{clean_text}"',
                                    f'text*="{clean_text}"',
                                    f'[aria-label*="{clean_text}"]'
                                ])
                            if target.role:
                                fallback_selectors.append(target.role)
                            
                            result, error = await self._try_multiple_selectors(page, fallback_selectors, "click", timeout_ms)
                            if "clicked" in result:
                                return result, None
                        
                        return "click_failed", e
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
                    try:
                        await page.locator(selector).first.fill(action.value, timeout=timeout_ms)
                        return "filled", None
                    except Exception as e:
                        # Try fallback selectors for form fields
                        target = action.target
                        if target:
                            fallback_selectors = []
                            if target.name:
                                fallback_selectors.extend([
                                    f'input[name="{target.name}"]',
                                    f'textarea[name="{target.name}"]',
                                    f'[name="{target.name}"]'
                                ])
                            if target.text:
                                clean_text = target.text.strip()
                                fallback_selectors.extend([
                                    f'input[placeholder*="{clean_text}"]',
                                    f'[aria-label*="{clean_text}"]'
                                ])
                            
                            for fallback_selector in fallback_selectors:
                                try:
                                    await page.locator(fallback_selector).first.fill(action.value, timeout=timeout_ms)
                                    return f"filled_with_{fallback_selector}", None
                                except:
                                    continue
                        
                        return "fill_failed", e
                return "selector_not_found_or_no_value", None
            
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
        """Build selector from action target with enhanced strategies."""
        if not action.target:
            return None
        
        target = action.target
        
        # Try different selector strategies in priority order
        selectors_to_try = []
        
        # Priority 1: Direct selector (if provided)
        if target.selector:
            selectors_to_try.append(target.selector)
        
        # Priority 2: Text-based selectors (most reliable)
        if target.text:
            # Clean the text and create multiple variants
            clean_text = target.text.strip()
            if clean_text:
                selectors_to_try.extend([
                    f'text="{clean_text}"',
                    f'text={clean_text}',
                    f'text*="{clean_text}"',  # Contains text
                    f'[aria-label*="{clean_text}"]',
                    f'[title*="{clean_text}"]'
                ])
        
        # Priority 3: Role and name combinations
        if target.role and target.name:
            selectors_to_try.extend([
                f'{target.role}[name="{target.name}"]',
                f'[role="{target.role}"][name="{target.name}"]'
            ])
        
        # Priority 4: Role-based selectors
        if target.role:
            role_selectors = {
                'button': ['button', '[role="button"]', '[type="button"]'],
                'link': ['a', '[role="link"]'],
                'input': ['input', '[role="textbox"]'],
                'select': ['select', '[role="combobox"]', '[role="listbox"]'],
                'textarea': ['textarea', '[role="textbox"]']
            }
            if target.role in role_selectors:
                selectors_to_try.extend(role_selectors[target.role])
        
        # Priority 5: Name-based selectors
        if target.name:
            selectors_to_try.extend([
                f'[name="{target.name}"]',
                f'[data-testid="{target.name}"]',
                f'[data-test="{target.name}"]',
                f'#{target.name}',
                f'.{target.name}'
            ])
        
        # Return the first available selector
        return selectors_to_try[0] if selectors_to_try else None
    
    async def _try_multiple_selectors(self, page: Page, selectors: List[str], action_type: str = "click", timeout_ms: int = 3000) -> Tuple[str, Optional[Exception]]:
        """Try multiple selector strategies until one works."""
        last_error = None
        
        for selector in selectors:
            if not selector:
                continue
                
            try:
                # Test if element exists and is visible
                element = page.locator(selector).first
                
                if action_type == "click":
                    await element.scroll_into_view_if_needed(timeout=timeout_ms)
                    await element.click(timeout=timeout_ms)
                    return f"clicked_with_{selector}", None
                elif action_type == "fill":
                    await element.scroll_into_view_if_needed(timeout=timeout_ms)
                    return f"found_element_{selector}", None
                    
            except Exception as e:
                last_error = e
                continue
        
        return "selector_failed", last_error