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
        run_id="test_nike_shopper_shoes",
        url="https://www.nike.com/",
        persona=Persona(
            name="Jordan",
            bio=(
                "Jordan is a 24-year-old college athlete who plays basketball and follows the latest sneaker drops. "
                "He cares about both performance and style, and he often browses Nike’s website to check out new releases. "
                "Jordan doesn’t like wasting time digging through menus—he wants to get straight to the newest basketball shoes. "
                "He’s budget-conscious as a student but will splurge on limited editions if they stand out."
            )
        ),
        ux_question=(
            "Navigate to the newest basketball shoe releases on Nike’s website so Jordan can browse the latest styles "
            "and decide if he wants to buy a pair."
        ),
        viewport=Viewport.DESKTOP,
        step_budget=12,
        max_consecutive_errors=3
    )
    
    test_case_2 = AgentInput(
        run_id="test_bbc_trending_news",
        url="https://www.bbc.com/",
        persona=Persona(
            name="Samantha",
            bio=(
                "Samantha is a 34-year-old marketing professional who likes to stay updated on global events "
                "during her morning coffee. She’s not very technical, prefers simple navigation, and usually "
                "looks for trending or top news stories without wanting to dig too deep. Samantha values speed, "
                "clarity, and a straightforward path to headlines."
            )
        ),
        ux_question=(
            "Find and click on today’s top trending news story on the BBC homepage so Samantha can quickly read it."
        ),
        viewport=Viewport.DESKTOP,
        step_budget=10,
        max_consecutive_errors=2
    )
        
    test_case_3 = AgentInput(
        run_id="test_imdb_movie_search",
        url="https://www.imdb.com/",
        persona=Persona(
            name="David",
            bio=(
                "David is a 27-year-old graduate student who loves movies and TV shows. He often checks IMDB "
                "to read reviews, watch trailers, and see ratings before deciding what to watch. David isn’t very "
                "technical but is comfortable browsing popular sites. Tonight, he wants to quickly look up a movie "
                "his friends recommended so he can decide whether it’s worth watching."
            )
        ),
        ux_question=(
            "Search for the movie 'Inception' on IMDB and open its page so David can check the rating, reviews, "
            "and cast information."
        ),
        viewport=Viewport.DESKTOP,
        step_budget=12,
        max_consecutive_errors=2
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