from typing import List
from playwright.async_api import Page
try:
    from ..models.schemas import PageDigest, PageElement
except ImportError:
    from models.schemas import PageDigest, PageElement


async def extract_page_digest(page: Page, max_interactives: int = 30) -> PageDigest:
    """Extract key information from a page for LLM planning."""
    
    # Get basic page info
    title = await page.title()
    url = page.url
    
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
    
    # Extract interactive elements
    interactives = await page.evaluate(f"""
        () => {{
            const elements = [];
            const selectors = [
                'button',
                'a[href]',
                'input:not([type="hidden"])',
                'select',
                'textarea',
                '[role="button"]',
                '[role="link"]',
                '[onclick]'
            ];
            
            const allElements = document.querySelectorAll(selectors.join(','));
            const visibleElements = [];
            
            allElements.forEach(el => {{
                const rect = el.getBoundingClientRect();
                const isVisible = rect.width > 0 && rect.height > 0 && 
                    window.getComputedStyle(el).display !== 'none' &&
                    window.getComputedStyle(el).visibility !== 'hidden';
                
                if (isVisible || el.offsetParent !== null) {{
                    visibleElements.push(el);
                }}
            }});
            
            visibleElements.slice(0, {max_interactives}).forEach(el => {{
                const element = {{
                    role: el.getAttribute('role') || el.tagName.toLowerCase(),
                    name: el.getAttribute('aria-label') || el.getAttribute('name'),
                    text: el.textContent ? el.textContent.trim().substring(0, 50) : null,
                    label: el.getAttribute('aria-label') || el.getAttribute('title'),
                    placeholder: el.getAttribute('placeholder'),
                    data_testid: el.getAttribute('data-testid'),
                    visible: true
                }};
                
                // Create selector hint
                let selector_hint = '';
                if (element.text && element.text.length > 2) {{
                    selector_hint = `text=${{element.text}}`;
                }} else if (element.role && element.name) {{
                    selector_hint = `${{element.role}}[name="${{element.name}}"]`;
                }} else if (element.data_testid) {{
                    selector_hint = `[data-testid="${{element.data_testid}}"]`;
                }} else if (el.id) {{
                    selector_hint = `#${{el.id}}`;
                }} else if (el.className) {{
                    selector_hint = `.${{el.className.split(' ')[0]}}`;
                }}
                
                element.selector_hint = selector_hint;
                elements.push(element);
            }});
            
            return elements;
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