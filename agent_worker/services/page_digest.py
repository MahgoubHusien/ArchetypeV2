from typing import List, Dict, Any
from playwright.async_api import Page
try:
    from ..models.schemas import PageDigest, PageElement
except ImportError:
    from models.schemas import PageDigest, PageElement


async def extract_page_digest(page: Page, max_interactives: int = 50) -> PageDigest:
    """Extract key information from a page for LLM planning with enhanced element detection."""
    
    # Get basic page info
    title = await page.title()
    url = page.url
    
    # Wait for page to be fully loaded
    try:
        await page.wait_for_load_state("domcontentloaded", timeout=3000)
        await page.wait_for_timeout(500)  # Small delay for dynamic content
    except:
        pass  # Continue even if timeout
    
    # Extract headings (H1/H2)
    headings = await page.evaluate("""
        () => {
            const headings = [];
            const h1s = document.querySelectorAll('h1');
            const h2s = document.querySelectorAll('h2');
            
            h1s.forEach(h => {
                if (h.textContent.trim()) {
                    headings.push(h.textContent.trim());
                }
            });
            
            h2s.forEach(h => {
                if (h.textContent.trim()) {
                    headings.push(h.textContent.trim());
                }
            });
            
            return headings.slice(0, 5);
        }
    """)
    
    # Extract interactive elements with enhanced detection
    interactives = await page.evaluate(f"""
        () => {{
            const elements = [];
            
            // Comprehensive selector list for all interactive elements
            const selectors = [
                'button',
                'a',
                'input:not([type="hidden"])',
                'select',
                'textarea',
                '[role="button"]',
                '[role="link"]',
                '[role="tab"]',
                '[role="menuitem"]',
                '[role="option"]',
                '[role="checkbox"]',
                '[role="radio"]',
                '[role="switch"]',
                '[role="slider"]',
                '[role="spinbutton"]',
                '[role="combobox"]',
                '[role="listbox"]',
                '[role="tree"]',
                '[role="grid"]',
                '[role="gridcell"]',
                '[role="columnheader"]',
                '[role="rowheader"]',
                '[onclick]',
                '[onmousedown]',
                '[onmouseup]',
                '[data-testid]',
                '[data-test]',
                '[data-cy]',
                '.btn',
                '.button',
                '.link',
                '.clickable',
                '[tabindex]',
                'form',
                'label',
                'img[onclick]',
                'div[onclick]',
                'span[onclick]',
                'li[onclick]',
                '[contenteditable="true"]'
            ];
            
            // Get all potential interactive elements
            const allElements = document.querySelectorAll(selectors.join(','));
            const processedElements = new Set();
            
            // Helper function to get element text content intelligently
            function getElementText(el) {{
                // Try different text sources
                let text = el.getAttribute('aria-label') || 
                          el.getAttribute('title') || 
                          el.getAttribute('alt') || 
                          el.getAttribute('placeholder') ||
                          el.value ||
                          '';
                
                if (!text) {{
                    // Get visible text content, handling special cases
                    text = el.textContent?.trim() || '';
                    
                    // For inputs, get the type and any associated labels
                    if (el.tagName === 'INPUT' && el.type) {{
                        const label = document.querySelector(`label[for="${{el.id}}"]`);
                        if (label) {{
                            text = label.textContent?.trim() || text;
                        }}
                    }}
                    
                    // For images, try alt text or nearby text
                    if (el.tagName === 'IMG') {{
                        text = el.alt || el.title || '';
                    }}
                }}
                
                return text.substring(0, 100);
            }}
            
            // Helper function to check if element is truly interactive
            function isInteractive(el) {{
                const tag = el.tagName.toLowerCase();
                const role = el.getAttribute('role');
                const type = el.getAttribute('type');
                
                // Standard interactive elements
                if (['button', 'a', 'input', 'select', 'textarea'].includes(tag)) {{
                    return true;
                }}
                
                // Elements with interactive roles
                if (role && ['button', 'link', 'tab', 'menuitem', 'option', 'checkbox', 'radio', 'switch'].includes(role)) {{
                    return true;
                }}
                
                // Elements with click handlers
                if (el.onclick || el.getAttribute('onclick')) {{
                    return true;
                }}
                
                // Elements with tabindex (focusable)
                if (el.hasAttribute('tabindex') && el.tabIndex >= 0) {{
                    return true;
                }}
                
                // Contenteditable elements
                if (el.contentEditable === 'true') {{
                    return true;
                }}
                
                // Check computed style for cursor pointer
                const style = window.getComputedStyle(el);
                if (style.cursor === 'pointer') {{
                    return true;
                }}
                
                return false;
            }}
            
            // Helper function to get parent context
            function getParentContext(el) {{
                let context = '';
                let parent = el.parentElement;
                let depth = 0;
                
                while (parent && depth < 3) {{
                    if (parent.tagName === 'FORM') {{
                        context = 'form: ' + (parent.getAttribute('name') || parent.id || 'unnamed');
                        break;
                    }}
                    if (parent.tagName === 'NAV') {{
                        context = 'navigation';
                        break;
                    }}
                    if (parent.classList.contains('menu') || parent.classList.contains('navbar')) {{
                        context = 'menu';
                        break;
                    }}
                    if (parent.getAttribute('role') === 'dialog' || parent.classList.contains('modal')) {{
                        context = 'modal/dialog';
                        break;
                    }}
                    parent = parent.parentElement;
                    depth++;
                }}
                
                return context;
            }}
            
            // Helper function to create robust selector
            function createRobustSelector(el) {{
                const selectors = [];
                
                // Priority 1: ID (most specific)
                if (el.id) {{
                    selectors.push(`#${{el.id}}`);
                }}
                
                // Priority 2: data-testid and test attributes
                if (el.getAttribute('data-testid')) {{
                    selectors.push(`[data-testid="${{el.getAttribute('data-testid')}}"]`);
                }}
                if (el.getAttribute('data-test')) {{
                    selectors.push(`[data-test="${{el.getAttribute('data-test')}}"]`);
                }}
                if (el.getAttribute('data-cy')) {{
                    selectors.push(`[data-cy="${{el.getAttribute('data-cy')}}"]`);
                }}
                
                // Priority 3: Text-based selectors (most reliable for users)
                const text = getElementText(el);
                if (text && text.length > 1 && text.length < 50) {{
                    // Escape quotes in text for Playwright
                    const escapedText = text.replace(/"/g, '\\\\"');
                    selectors.push(`text="${{escapedText}}"`);
                    if (el.tagName.toLowerCase() === 'button') {{
                        selectors.push(`button:has-text("${{escapedText}}")`);
                    }}
                    if (el.tagName.toLowerCase() === 'a') {{
                        selectors.push(`a:has-text("${{escapedText}}")`);
                    }}
                }}
                
                // Priority 4: Role + name combinations
                const role = el.getAttribute('role') || el.tagName.toLowerCase();
                const name = el.getAttribute('name');
                if (role && name) {{
                    selectors.push(`${{role}}[name="${{name}}"]`);
                }}
                
                // Priority 5: Attribute-based selectors
                if (el.getAttribute('aria-label')) {{
                    selectors.push(`[aria-label="${{el.getAttribute('aria-label')}}"]`);
                }}
                if (el.getAttribute('title')) {{
                    selectors.push(`[title="${{el.getAttribute('title')}}"]`);
                }}
                if (el.getAttribute('placeholder')) {{
                    selectors.push(`[placeholder="${{el.getAttribute('placeholder')}}"]`);
                }}
                
                // Priority 6: Class-based (less reliable but sometimes necessary)
                if (el.className && typeof el.className === 'string') {{
                    const classes = el.className.split(' ').filter(c => c && !c.includes('css-') && !c.match(/^[a-z0-9]{{6,}}$/));
                    if (classes.length > 0) {{
                        selectors.push(`.${{classes[0]}}`);
                    }}
                }}
                
                // Priority 7: Tag + attribute combinations
                if (el.tagName.toLowerCase() === 'input' && el.type) {{
                    selectors.push(`input[type="${{el.type}}"]`);
                }}
                if (el.href) {{
                    selectors.push(`a[href="${{el.href}}"]`);
                }}
                
                return selectors[0] || el.tagName.toLowerCase();
            }}
            
            // Process all elements
            allElements.forEach(el => {{
                // Skip if already processed (avoid duplicates)
                if (processedElements.has(el)) return;
                processedElements.add(el);
                
                // Check visibility
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                const isVisible = rect.width > 0 && rect.height > 0 && 
                    style.display !== 'none' &&
                    style.visibility !== 'hidden' &&
                    style.opacity !== '0';
                
                // Check if truly interactive
                if (!isInteractive(el)) return;
                
                const text = getElementText(el);
                const tag = el.tagName.toLowerCase();
                
                const element = {{
                    // Basic properties
                    role: el.getAttribute('role') || tag,
                    name: el.getAttribute('name'),
                    text: text || null,
                    label: el.getAttribute('aria-label'),
                    placeholder: el.getAttribute('placeholder'),
                    data_testid: el.getAttribute('data-testid'),
                    visible: isVisible,
                    
                    // Enhanced properties
                    element_id: el.id || null,
                    class_name: el.className || null,
                    tag_name: tag,
                    href: el.href || null,
                    type: el.type || null,
                    value: el.value || null,
                    aria_label: el.getAttribute('aria-label'),
                    title: el.getAttribute('title'),
                    alt: el.getAttribute('alt'),
                    position: isVisible ? {{
                        x: Math.round(rect.x),
                        y: Math.round(rect.y),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    }} : null,
                    parent_context: getParentContext(el),
                    clickable: (['button', 'a'].includes(tag) || el.onclick || el.getAttribute('onclick') || style.cursor === 'pointer') || false,
                    focusable: (el.tabIndex >= 0 || ['input', 'select', 'textarea', 'button', 'a'].includes(tag)) || false,
                    form_field: ['input', 'select', 'textarea'].includes(tag) || false,
                    selector_hint: createRobustSelector(el)
                }};
                
                elements.push(element);
            }});
            
            // Sort by visibility and position (top-left first)
            elements.sort((a, b) => {{
                if (a.visible && !b.visible) return -1;
                if (!a.visible && b.visible) return 1;
                if (a.position && b.position) {{
                    if (a.position.y !== b.position.y) return a.position.y - b.position.y;
                    return a.position.x - b.position.x;
                }}
                return 0;
            }});
            
            return elements.slice(0, {max_interactives});
        }}
    """)
    
    # Convert to Pydantic models
    page_elements = [PageElement(**el) for el in interactives]
    
    return PageDigest(
        title=title,
        url=url,
        headings=headings,
        interactives=page_elements
    )


async def get_element_context(page: Page, selector: str) -> Dict[str, Any]:
    """Get additional context about a specific element for better targeting."""
    try:
        element_info = await page.evaluate(f"""
            (selector) => {{
                const el = document.querySelector(selector);
                if (!el) return null;
                
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                
                return {{
                    text: el.textContent?.trim(),
                    value: el.value,
                    checked: el.checked,
                    disabled: el.disabled,
                    visible: rect.width > 0 && rect.height > 0 && style.display !== 'none',
                    position: {{ x: rect.x, y: rect.y, width: rect.width, height: rect.height }},
                    attributes: Array.from(el.attributes).reduce((acc, attr) => {{
                        acc[attr.name] = attr.value;
                        return acc;
                    }}, {{}})
                }};
            }}
        """, selector)
        
        return element_info or {"error": "Element not found"}
    except Exception as e:
        return {"error": str(e)}


async def validate_interactive_elements(page: Page, elements: List[PageElement]) -> List[PageElement]:
    """Validate that detected interactive elements are still present and accessible."""
    validated_elements = []
    
    for element in elements:
        if not element.selector_hint:
            continue
            
        try:
            # Check if element still exists and is interactable
            is_valid = await page.evaluate(f"""
                (selector) => {{
                    const el = document.querySelector(selector);
                    if (!el) return false;
                    
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    
                    return rect.width > 0 && rect.height > 0 && 
                           style.display !== 'none' && 
                           style.visibility !== 'hidden' &&
                           !el.disabled;
                }}
            """, element.selector_hint)
            
            if is_valid:
                validated_elements.append(element)
                
        except:
            # If validation fails, skip this element
            continue
    
    return validated_elements


def filter_elements_by_type(elements: List[PageElement], element_type: str) -> List[PageElement]:
    """Filter elements by type (clickable, form_field, focusable, etc.)."""
    if element_type == "clickable":
        return [el for el in elements if el.clickable]
    elif element_type == "form_field":
        return [el for el in elements if el.form_field]
    elif element_type == "focusable":
        return [el for el in elements if el.focusable]
    elif element_type == "visible":
        return [el for el in elements if el.visible]
    else:
        return elements


def get_element_summary(digest: PageDigest) -> Dict[str, Any]:
    """Get a summary of the page elements for debugging and analysis."""
    total_elements = len(digest.interactives)
    visible_elements = len([el for el in digest.interactives if el.visible])
    clickable_elements = len([el for el in digest.interactives if el.clickable])
    form_elements = len([el for el in digest.interactives if el.form_field])
    
    element_types = {}
    for element in digest.interactives:
        tag = element.tag_name or "unknown"
        element_types[tag] = element_types.get(tag, 0) + 1
    
    return {
        "page_title": digest.title,
        "page_url": digest.url,
        "headings": len(digest.headings),
        "total_interactive_elements": total_elements,
        "visible_elements": visible_elements,
        "clickable_elements": clickable_elements,
        "form_elements": form_elements,
        "element_types": element_types,
        "has_navigation": any("nav" in str(el.parent_context).lower() for el in digest.interactives if el.parent_context),
        "has_forms": any("form" in str(el.parent_context).lower() for el in digest.interactives if el.parent_context),
        "has_modals": any("modal" in str(el.parent_context).lower() for el in digest.interactives if el.parent_context)
    }