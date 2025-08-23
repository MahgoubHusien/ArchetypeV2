"""
Test with example.com to verify the agent is working properly
"""
import asyncio
import os
from dotenv import load_dotenv
from models.schemas import AgentInput, Persona, Viewport
from agent import UXAgent
from utils.storage import TranscriptStorage

load_dotenv()


async def test_example():
    """Test agent on example.com."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ Please set OPENAI_API_KEY in .env file")
        return
    
    # Create test input
    test_input = AgentInput(
        run_id="example_test_001",
        url="https://example.com",
        persona=Persona(
            name="Test User",
            bio="Curious user exploring the website"
        ),
        ux_question="Is the page content clear and easy to understand?",
        viewport=Viewport.DESKTOP,
        step_budget=6,
        max_consecutive_errors=2,
        seed=42
    )
    
    print(f"Running agent test on example.com...")
    print(f"Persona: {test_input.persona.name}")
    print(f"Question: {test_input.ux_question}")
    print(f"Step budget: {test_input.step_budget}")
    
    # Run agent
    agent = UXAgent(api_key)
    result = await agent.run(test_input)
    
    # Save results
    storage = TranscriptStorage()
    filepath = await storage.save_transcript(test_input.run_id, result)
    
    print(f"\n✅ Test completed!")
    print(f"Status: {result.finish_reason}")
    print(f"Steps taken: {len(result.interactions)}")
    print(f"Transcript: {filepath}")
    
    # Print interactions
    print("\nInteractions:")
    for interaction in result.interactions:
        print(f"  Step {interaction.step}: {interaction.intent}")
        print(f"    Action: {interaction.action_type.value}")
        print(f"    Result: {interaction.result}")
        if interaction.selector:
            print(f"    Selector: {interaction.selector}")


if __name__ == "__main__":
    asyncio.run(test_example())