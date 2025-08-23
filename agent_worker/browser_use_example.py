"""
Example of how to integrate browser-use for the agent worker.
This shows the alternative approach using the browser-use library.
"""

import asyncio
from browser_use import AsyncAgent, BrowserType
from models.schemas import AgentInput, Persona, Viewport


async def run_with_browser_use(agent_input: AgentInput):
    """Example of running agent with browser-use library."""
    
    # Initialize browser-use agent
    browser_type = BrowserType.CHROMIUM
    
    # Create agent with custom system prompt for UX testing
    system_prompt = f"""
    You are a UX testing agent simulating the following persona:
    Name: {agent_input.persona.name}
    Bio: {agent_input.persona.bio}
    
    Your task is to browse the website and answer this UX question:
    {agent_input.ux_question}
    
    Take up to {agent_input.step_budget} actions to explore and understand the UI.
    Focus on the specific UI element or flow mentioned in the question.
    """
    
    async with AsyncAgent(
        browser_type=browser_type,
        system_prompt=system_prompt,
        max_actions=agent_input.step_budget,
        headless=True,
        viewport_size=(393, 852) if agent_input.viewport == Viewport.MOBILE else (1920, 1080)
    ) as agent:
        
        # Navigate and perform task
        result = await agent.run(agent_input.url)
        
        # Extract interactions from browser-use history
        interactions = []
        for i, action in enumerate(result.actions):
            interactions.append({
                "step": i + 1,
                "intent": action.intent,
                "action_type": action.type,
                "selector": action.selector,
                "result": action.result,
                "screenshot": action.screenshot_path,
                "thought": action.reasoning
            })
        
        return {
            "persona": agent_input.persona,
            "interactions": interactions,
            "finish_reason": result.completion_reason,
            "insights": result.final_response
        }


async def demo():
    """Demo of browser-use integration."""
    demo_input = AgentInput(
        run_id="browser_use_demo",
        url="https://www.etsy.com",
        persona=Persona(
            name="Sarah",
            bio="35-year-old teacher looking for classroom decorations"
        ),
        ux_question="Is the search functionality easily discoverable on mobile?",
        viewport=Viewport.MOBILE,
        step_budget=5
    )
    
    print("Running browser-use demo...")
    result = await run_with_browser_use(demo_input)
    
    print(f"\nPersona: {result['persona'].name}")
    print(f"Interactions: {len(result['interactions'])}")
    print(f"Completion: {result['finish_reason']}")
    print(f"\nInsights: {result['insights']}")


if __name__ == "__main__":
    # Note: This is a conceptual example showing how browser-use 
    # could be integrated. The actual browser-use API might differ.
    print("This is a conceptual example of browser-use integration.")
    print("Refer to browser-use documentation for actual implementation.")