import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from agent import UXAgent
from models.schemas import AgentInput, Persona, Viewport
from utils.storage import TranscriptStorage

load_dotenv()


async def test_bug_detection():
    """Test the bug detection and sentiment analysis features."""
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY in .env file")
        return
    
    # Test case 1: Buggy website with frustrated user
    test_case_1 = AgentInput(
        run_id="test_bugs_frustrated_12",
        url="https://www.ycombinator.com/",
        persona=Persona(
            name="Alex",
            bio="Impatient user who wants quick results and hates broken websites"
        ),
        ux_question="Can I find contact information quickly?",
        viewport=Viewport.DESKTOP,
        step_budget=10,
        max_consecutive_errors=3
    )
    
    # Test case 2: Normal website with engaged user
    test_case_2 = AgentInput(
        run_id="test_normal_engaged_12",
        url="https://www.airbnb.com/",
        persona=Persona(
            name="Sarah",
            bio="Curious researcher interested in web standards and documentation"
        ),
        ux_question="What information does this site provide?",
        viewport=Viewport.DESKTOP,
        step_budget=5
    )
    
    test_case_3 = AgentInput(
    run_id="test_hackernews_startups",
    url="https://news.ycombinator.com/",
    persona=Persona(
        name="Jake",
        bio=(
            "Jake is a 30-year-old founder exploring YC-funded startups. "
            "He's on Hacker News to read trending discussions about new AI companies."
        )
    ),
    ux_question="Find and click on the top AI-related startup post on Hacker News.",
    viewport=Viewport.DESKTOP,
    step_budget=15
)

    print("Running bug detection and sentiment analysis tests...\n")
    
    for i, test_case in enumerate([test_case_1, test_case_2, test_case_3], 1):
        print(f"=== Test Case {i}: {test_case.run_id} ===")
        print(f"Persona: {test_case.persona.name} - {test_case.persona.bio}")
        print(f"Testing: {test_case.url}")
        print(f"Question: {test_case.ux_question}")
        
        agent = UXAgent(api_key)
        result = await agent.run(test_case)
        
        print(f"\nResults:")
        print(f"- Finish reason: {result.finish_reason}")
        print(f"- Overall sentiment: {result.overall_sentiment}")
        print(f"- Bugs encountered: {result.bugs_encountered}")
        if result.dropoff_reason:
            print(f"- Dropoff reason: {result.dropoff_reason}")
        
        # Show sentiment progression
        sentiments = [i.sentiment for i in result.interactions]
        print(f"- Sentiment progression: {' -> '.join(sentiments)}")
        
        # Show bugs
        bugs = [(i.step, i.bug_type, i.bug_description) 
                for i in result.interactions if i.bug_detected]
        if bugs:
            print("- Bugs found:")
            for step, bug_type, desc in bugs:
                print(f"  Step {step}: {bug_type} - {desc}")
        
        # Save transcript
        storage = TranscriptStorage()
        filepath = await storage.save_transcript(test_case.run_id, result)
        print(f"- Transcript saved to: {filepath}\n")


if __name__ == "__main__":
    asyncio.run(test_bug_detection())