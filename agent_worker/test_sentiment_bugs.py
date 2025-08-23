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
        run_id="test_slack_frustrated_contact",
        url="https://slack.com/",
        persona=Persona(
            name="Alex",
            bio=(
                "Alex is a 29-year-old design lead at a fast-paced agency. They’re under a tight deadline to "
                "evaluate Slack for a companywide rollout. Alex expects clear calls-to-action, visible enterprise "
                "contact info, and quick navigation. They dislike hidden or slow UX, and if primary paths fail, "
                "they’ll try search, footer links, or support pages before growing annoyed."
            )
        ),
        ux_question=(
            "Find and click the most straightforward way to contact Slack’s enterprise or sales team—whether it's "
            "'Contact sales', 'Request a demo', or a dedicated enterprise support link. Prefer top navigation CTAs; "
            "if not obvious, check the footer or help section. Open that page so Alex can send a message immediately."
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
        run_id="test_neetcode_practice_2sum_2",
        url="https://neetcode.io/",
        persona=Persona(
            name="Jake",
            bio=(
                "Jake is a 30-year-old software engineer preparing for a big FAANG interview. "
                "He knows that success will require mastering common algorithmic problems, "
                "and he is determined to practice daily on NeetCode. With only a few weeks "
                "before his interview, Jake feels a sense of urgency and wants to start practicing "
                "immediately. He is focusing on essential problems like 2 Sum, which often appear "
                "in coding assessments. Highly motivated and disciplined, Jake is eager to quickly "
                "strengthen his problem-solving speed and accuracy."
            )
        ),
        ux_question="Quickly locate and click on the 2 Sum problem on NeetCode so Jake can begin practicing it right away for his upcoming FAANG interview.",
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