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
    
    # Test case 2: YC investor scouting startups (detailed persona + goal)
    test_case_2 = AgentInput(
        run_id="test_yc_investor_startups",
        url="https://www.ycombinator.com/companies",
        persona=Persona(
            name="Noah",
            bio=(
                "Noah is a 33-year-old angel investor (ex-staff engineer, 2x founder exit) with a $500k allocation this quarter. "
                "His thesis prioritizes AI (infra + applied), developer tooling (product-led growth, bottom-up adoption), and fintech "
                "(compliance-forward, clear revenue paths). Noah screens for: recent YC batches (S23+), active hiring signals, early "
                "traction (paying customers or credible pilots), concise problem statements, and clear links (website, careers, LinkedIn). "
                "He prefers US/EU time zones for hands-on support, and teams with technical founders who can ship quickly. "
                "Initial pass criteria: crisp positioning, plausible GTM, and ability to reach $1–3M ARR in 18–24 months. "
                "Secondary diligence: founder backgrounds (LinkedIn/GitHub), demo walkthroughs, pricing pages, and signs of ICP clarity. "
                "Goal today: identify a fintech company (Stripe-like or in financial services) on YC’s directory to review in detail."
            )
        ),
        ux_question=(
            "On YC’s Companies directory, filter for Fintech startups. "
            "Scroll through the results and explicitly select one fintech company (for example, Stripe or a similar financial startup). "
            "Open its YC profile page, review the description, and then click through to its external website. "
            "Do not remain in browse mode — you must pick one fintech company and go inside its profile. "
            "Stay on that startup’s YC company page at the end so Noah can capture it for investment notes."
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
            name="Leila",
            bio=(
                "Leila is a 28-year-old product designer who commutes daily and needs a lightweight, packable jacket "
                "for cool mornings. She prefers clean, minimal sites with clear categories and fast paths to product "
                "details. Leila wants a black women’s lightweight down jacket, and she needs to quickly verify price, "
                "available sizes, and nearby store availability before deciding."
            )
        ),
        ux_question=(
            "On Uniqlo’s website, navigate to Women → Outerwear (or similar), locate a lightweight down jacket in black, "
            "and open a product detail page. Confirm the price is visible and check size availability (aim for size M). "
            "If a store availability or pickup option is shown, open it."
        ),
        viewport=Viewport.DESKTOP,
        step_budget=12,
        max_consecutive_errors=3
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