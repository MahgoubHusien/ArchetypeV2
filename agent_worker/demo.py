import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from agent import UXAgent
from models.schemas import AgentInput, Persona, Viewport
from utils.storage import TranscriptStorage

load_dotenv()


async def run_demo():
    """Run a demo of the UX agent."""
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY in .env file")
        return
    
    # Create demo input
    demo_input = AgentInput(
        run_id="buggy_demo_001",
        url="https://buggy.justtestit.org/",
        persona=Persona(
            name="Sam",
            bio="26-year-old kid runs into a website and wants to know what it is"
        ),
        ux_question="What is this website about?",
        viewport=Viewport.DESKTOP,
        step_budget=15,
        max_consecutive_errors=2,
        seed=19
    )


    
    print(f"Starting UX test agent...")
    print(f"Persona: {demo_input.persona.name} - {demo_input.persona.bio}")
    print(f"Testing: {demo_input.url}")
    print(f"Question: {demo_input.ux_question}")
    print(f"Budget: {demo_input.step_budget} steps\n")
    
    # Run agent
    agent = UXAgent(api_key)
    result = await agent.run(demo_input)
    
    # Save transcript
    storage = TranscriptStorage()
    filepath = await storage.save_transcript(demo_input.run_id, result)
    
    print(f"\nAgent completed with status: {result.finish_reason}")
    print(f"Total interactions: {len(result.interactions)}")
    print(f"Overall sentiment: {result.overall_sentiment}")
    print(f"Bugs encountered: {result.bugs_encountered}")
    if result.dropoff_reason:
        print(f"Dropoff reason: {result.dropoff_reason}")
    print(f"Transcript saved to: {filepath}")
    
    # Print interactions summary
    print("\nInteraction Summary:")
    for interaction in result.interactions:
        print(f"Step {interaction.step}: {interaction.intent}")
        print(f"  Action: {interaction.action_type.value}")
        print(f"  Thought: {interaction.thought}")
        print(f"  Sentiment: {interaction.sentiment}")
        if interaction.user_feeling:
            print(f"  Feeling: {interaction.user_feeling}")
        if interaction.bug_detected:
            print(f"  🐛 Bug detected: {interaction.bug_type} - {interaction.bug_description}")
        print(f"  Result: {interaction.result}")
        print(f"  Screenshot: {interaction.screenshot}")
        print()


if __name__ == "__main__":
    asyncio.run(run_demo())