import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.schemas import AgentInput, Persona, Viewport, PageDigest, PageElement
from services.planner import LLMPlanner, PLANNER_SYSTEM_MESSAGE


async def test_models():
    """Test that models work correctly."""
    print("Testing models...")
    
    # Test creating models
    persona = Persona(name="Test User", bio="A test user")
    agent_input = AgentInput(
        run_id="test_001",
        url="https://example.com",
        persona=persona,
        ux_question="Is the button clear?",
        viewport=Viewport.MOBILE
    )
    
    print(f"✓ Created AgentInput: {agent_input.run_id}")
    print(f"✓ Persona: {agent_input.persona.name}")
    print(f"✓ Viewport: {agent_input.viewport.value}")


async def test_page_digest():
    """Test page digest creation."""
    print("\nTesting page digest...")
    
    # Create sample page digest
    page_digest = PageDigest(
        title="Test Page",
        url="https://example.com",
        headings=["Welcome", "Features"],
        interactives=[
            PageElement(
                role="button",
                name="Submit",
                text="Submit Form",
                selector_hint="text=Submit Form"
            )
        ]
    )
    
    print(f"✓ Created PageDigest: {page_digest.title}")
    print(f"✓ Headings: {len(page_digest.headings)}")
    print(f"✓ Interactive elements: {len(page_digest.interactives)}")


async def test_planner():
    """Test LLM planner initialization."""
    print("\nTesting planner...")
    
    api_key = os.getenv("ANTHROPIC_API_KEY", "test_key")
    planner = LLMPlanner(api_key)
    
    print(f"✓ Created LLMPlanner")
    print(f"✓ System message length: {len(PLANNER_SYSTEM_MESSAGE)}")


async def main():
    """Run all tests."""
    print("Running Agent Worker Tests\n" + "="*40)
    
    await test_models()
    await test_page_digest()
    await test_planner()
    
    print("\n" + "="*40)
    print("All tests passed! ✅")


if __name__ == "__main__":
    asyncio.run(main())