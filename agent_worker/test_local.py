"""
Test with a simple local HTML page (no external dependencies)
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from models.schemas import AgentInput, Persona, Viewport
from agent import UXAgent
from utils.storage import TranscriptStorage

load_dotenv()


async def create_test_page():
    """Create a simple test HTML page."""
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test UX Page</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial; padding: 20px; }
            .hero { background: #f0f0f0; padding: 40px; text-align: center; }
            .cta-button { 
                background: #007bff; 
                color: white; 
                padding: 15px 30px; 
                border: none; 
                font-size: 18px; 
                cursor: pointer; 
                margin: 20px;
            }
            .unclear-button {
                background: #6c757d;
                color: white;
                padding: 10px 20px;
                border: none;
                margin: 10px;
            }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>Welcome to Our Product</h1>
            <h2>The best solution for your needs</h2>
            <button class="cta-button">Get Started Now</button>
        </div>
        
        <section>
            <h2>Features</h2>
            <p>Our product helps you accomplish amazing things.</p>
            <button class="unclear-button">Edit with AI</button>
            <button class="unclear-button">Enhance</button>
            <button class="unclear-button">Process</button>
        </section>
    </body>
    </html>
    """
    
    # Save test page
    test_file = Path("test_page.html")
    test_file.write_text(test_html)
    return test_file.absolute()


async def test_local():
    """Run agent on local test page."""
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ Please set OPENAI_API_KEY in .env file")
        return
    
    # Create test page
    test_url = await create_test_page()
    print(f"Created test page: {test_url}")
    
    # Create test input
    test_input = AgentInput(
        run_id="local_test_001",
        url=f"file://{test_url}",
        persona=Persona(
            name="Sarah",
            bio="Non-technical user trying to understand what the buttons do"
        ),
        ux_question="Are the button labels clear and descriptive?",
        viewport=Viewport.MOBILE,
        step_budget=4
    )
    
    print(f"\nRunning agent test...")
    print(f"Persona: {test_input.persona.name}")
    print(f"Question: {test_input.ux_question}")
    
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
    
    # Clean up
    test_url.unlink()


if __name__ == "__main__":
    asyncio.run(test_local())