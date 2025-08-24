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
            name="Meredith",
            bio=(
                "Meredith is a 78-year-old retired teacher who just started doing water aerobics at the local community center. "
                "She's not very tech-savvy and finds most websites overwhelming with too many options and small text. "
                "Meredith needs supportive shoes for her new exercise routine but gets frustrated when websites have complex navigation."
            )
        ),
        ux_question=(
            "Find the newest basketball shoe releases on Nike's website. Navigate through the site to locate "
            "the basketball shoes section and view the latest releases available."
        ),
        viewport=Viewport.DESKTOP,
        step_budget=12,
        max_consecutive_errors=3
    )
    
    # Test case 2: YC investor → MUST click the Website link
    test_case_2 = AgentInput(
    run_id="test_yc_investor_any_startup",
    url="https://www.ycombinator.com/companies",
    persona=Persona(
        name="Priya",
        bio=(
            "Priya is a 22-year-old coding bootcamp student from Mumbai who's fascinated by Silicon Valley startup culture. "
            "She browses Y Combinator to learn about successful companies and get inspiration for her own future startup ideas. "
            "Priya is extremely tech-savvy but English is her second language, so she sometimes needs clear, simple navigation."
        )
    ),
    ux_question=(
        "Browse the YC Companies directory and select any startup from the list to view its profile. "
        "Once on the startup's YC profile page, find and click the 'Website' link to visit the company's actual website. "
        "Stop once you successfully reach the startup's external website."
    ),
    viewport=Viewport.DESKTOP,
    step_budget=15,
    max_consecutive_errors=3
)
    # Test case 3: Uniqlo shopper finding a specific jacket (replacing Zara)
    test_case_3 = AgentInput(
        run_id="test_uniqlo_find_jacket",
        url="https://www.uniqlo.com/",
        persona=Persona(
            name="Hector",
            bio=(
                "Hector is a 41-year-old construction foreman who works outdoors in Colorado. "
                "He's practical and no-nonsense, preferring to shop quickly without browsing around. "
                "Hector needs a warm, durable jacket for the winter season and doesn't care about fashion trends—just functionality."
            )
        ),
        ux_question=(
            "Navigate to the Women's Outerwear section on Uniqlo's website and find a lightweight down jacket in black. "
            "Click on a specific product to view its details, including price and size availability (looking for size M). "
            "Stop once you can see the product details with pricing and size options."
        ),
        viewport=Viewport.DESKTOP,
        step_budget=12,
        max_consecutive_errors=3
    )

    # Test case 4: Wikipedia article search - clear success target
    test_case_4 = AgentInput(
        run_id="test_wikipedia_research",
        url="https://www.wikipedia.org/",
        persona=Persona(
            name="Amara",
            bio=(
                "Amara is a 16-year-old high school student in Nairobi working on a science project about artificial intelligence. "
                "She's extremely comfortable with technology, having grown up with smartphones and social media. "
                "Amara expects websites to load fast and gets impatient with slow or confusing interfaces."
            )
        ),
        ux_question=(
            "Search for 'Artificial Intelligence' on Wikipedia and navigate to the main article page. "
            "Stop once you reach the AI article showing the introduction and table of contents."
        ),
        viewport=Viewport.DESKTOP,
        step_budget=8,
        max_consecutive_errors=2
    )

    # Test case 5: IMDb movie search - test stopping after finding info
    test_case_5 = AgentInput(
        run_id="test_imdb_movie_search",
        url="https://www.imdb.com/",
        persona=Persona(
            name="Giuseppe",
            bio=(
                "Giuseppe is a 58-year-old Italian chef who owns a small trattoria in Rome. "
                "He recently got his first smartphone and is still learning to use websites properly. "
                "Giuseppe loves classic American movies and wants to look up information about his favorite actors, but he finds English websites challenging to navigate."
            )
        ),
        ux_question=(
            "Search for the movie 'Inception' on IMDB and find its main page with rating, plot summary, and cast information. "
            "Stop once you reach the movie's main page showing these details."
        ),
        viewport=Viewport.DESKTOP,
        step_budget=8,
        max_consecutive_errors=2
    )

    print("Running bug detection and sentiment analysis tests...\n")
    
    for i, test_case in enumerate([test_case_1, test_case_2, test_case_3, test_case_4, test_case_5], 1):
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