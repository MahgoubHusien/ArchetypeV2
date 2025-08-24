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
                target = action.target
                if not target:
                    return "no_target_provided", None
                
                # Get all possible selectors for this target
                all_selectors = self._get_all_possible_selectors(target)
                
                # Try each selector in order of reliability
                for selector in all_selectors:
                    try:
                        element = page.locator(selector).first
                        # Wait a moment for dynamic content
                        await page.wait_for_timeout(100)
                        
                        # Check if element exists and is visible
                        count = await element.count()
                        if count > 0:
                            # Check if element is visible
                            is_visible = await element.is_visible()
                            if is_visible:
                                await element.scroll_into_view_if_needed(timeout=timeout_ms)
                                # Double-check visibility after scroll
                                is_still_visible = await element.is_visible()
                                if is_still_visible:
                                    await element.click(timeout=timeout_ms)
                                    return f"clicked_with_{selector}", None
                    except Exception as e:
                        continue
                
                # If all selectors failed, try one more strategy: find any clickable element with similar text
                if target.text:
                    try:
                        clean_text = target.text.strip()
                        # Try to find any element that contains the text and is clickable
                        all_elements = page.locator(f'text*="{clean_text}"')
                        count = await all_elements.count()
                        
                        for i in range(min(count, 5)):  # Check first 5 matches
                            element = all_elements.nth(i)
                            try:
                                is_visible = await element.is_visible()
                                if is_visible:
                                    await element.scroll_into_view_if_needed(timeout=timeout_ms)
                                    await element.click(timeout=timeout_ms)
                                    return "clicked_with_text_search", None
                            except:
                                continue
                    except:
                        pass
                
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
                    # Wait a bit more for dynamic content to load
                    await page.wait_for_timeout(1000)
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
        """Build selector from action target with enhanced reliability."""
        if not action.target:
            return None
        
        target = action.target
        
        # Priority 1: Use direct selector if provided
        if target.selector:
            return target.selector
        
        # Priority 2: Text-based selectors (most reliable for users)
        if target.text and len(target.text.strip()) > 0:
            clean_text = target.text.strip()
            # For links, try link-specific selectors first
            if target.role in ['link', 'a']:
                return f'a:has-text("{clean_text}")'
            # For buttons, try button-specific selectors
            elif target.role == 'button':
                return f'button:has-text("{clean_text}")'
            # General text selector
            else:
                return f'text="{clean_text}"'
        
        # Priority 3: Role and name combinations
        if target.role and target.name:
            return f'{target.role}[name="{target.name}"]'
        
        # Priority 4: Role-only selectors
        if target.role:
            return target.role
        
        # Priority 5: Name-only selectors
        if target.name:
            return f'[name="{target.name}"]'
        
        return None
    
    def _get_all_possible_selectors(self, target) -> List[str]:
        """Generate all possible selectors for a target, ordered by reliability."""
        selectors = []
        
        # Direct selector
        if target.selector:
            selectors.append(target.selector)
        
        # Text-based selectors
        if target.text and len(target.text.strip()) > 0:
            clean_text = target.text.strip()
            selectors.extend([
                f'text="{clean_text}"',
                f'text*="{clean_text}"',
                f'*:has-text("{clean_text}")',
                f'a:has-text("{clean_text}")',
                f'button:has-text("{clean_text}")',
                f'[aria-label*="{clean_text}"]',
                f'[title*="{clean_text}"]',
                f'[alt*="{clean_text}"]'
            ])
        
        # Role-based selectors
        if target.role:
            if target.role in ["button"]:
                selectors.extend(['button', '[role="button"]', '[type="button"]', '[type="submit"]', '.btn', '.button'])
            elif target.role in ["link", "a"]:
                selectors.extend(['a', '[role="link"]', 'a[href]'])
            else:
                selectors.extend([target.role, f'[role="{target.role}"]'])
        
        # Name-based selectors
        if target.name:
            selectors.extend([
                f'[name="{target.name}"]',
                f'#{target.name}',
                f'[data-testid="{target.name}"]',
                f'[data-test="{target.name}"]',
                f'[data-cy="{target.name}"]'
            ])
        
        # Generic fallbacks
        selectors.extend(['a', 'button', '[role="button"]', '[role="link"]'])
        
        # Remove duplicates while preserving order
        seen = set()
        return [x for x in selectors if not (x in seen or seen.add(x))]
    
