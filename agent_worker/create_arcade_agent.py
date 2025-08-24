#!/usr/bin/env python3
"""
Create an Agent for Testing Arcade.ai's "Create with AI" Feature

This script demonstrates how to create an agent to test the AI product creation
functionality on Arcade's platform.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from agent import UXAgent
from models.schemas import AgentInput, Persona, Viewport
from services.agent_manager import AgentManager

load_dotenv()


async def create_arcade_ai_agent():
    """Create an agent to test Arcade.ai's Create with AI functionality"""
    
    print("🎨 Creating Arcade.ai Agent for 'Create with AI' Testing")
    print("=" * 55)
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY in .env file")
        return
    
    # Initialize the agent manager
    agent_manager = AgentManager(Path("data"))
    
    # Create a persona interested in AI-powered product creation
    persona = Persona(
        name="Maya",
        bio=(
            "Maya is a 31-year-old interior designer and entrepreneur who runs a boutique "
            "home decor business. She's tech-savvy and always looking for innovative ways to "
            "expand her product offerings. Maya has heard about AI-powered design tools and "
            "is curious about how they could help her create unique products for her clients. "
            "She's particularly interested in custom furniture and decorative objects that "
            "can be personalized. Maya values efficiency and quality, and she's excited about "
            "the possibility of offering instant customizations to her customers without "
            "the usual back-and-forth communication."
        )
    )
    
    # Define the test scenario
    agent_input = AgentInput(
        run_id="arcade_ai_test_001",
        url="https://www.arcade.ai/sell",
        persona=persona,
        ux_question=(
            "I'm an interior designer interested in joining Arcade as a seller. I want to "
            "explore the 'Create with AI' feature to understand how it works for product creation. "
            "Navigate to the Create with AI section, explore the interface, and try to understand "
            "the process for creating AI-generated products. Stop once you've successfully "
            "accessed and explored the main Create with AI functionality."
        ),
        viewport=Viewport.DESKTOP,
        step_budget=15,
        max_consecutive_errors=3
    )
    
    print(f"👤 Persona: {persona.name}")
    print(f"📝 Bio: {persona.bio[:150]}...")
    print(f"🌐 Target URL: {agent_input.url}")
    print(f"❓ Test Objective: Explore 'Create with AI' feature")
    print(f"📊 Step Budget: {agent_input.step_budget}")
    
    # Create and run the agent
    print(f"\n🚀 Launching Agent...")
    
    try:
        # Initialize UX Agent with the agent manager
        agent = UXAgent(api_key, agent_manager=agent_manager)
        
        # Run the agent
        result = await agent.run(agent_input)
        
        # Display results
        print(f"\n📊 RESULTS SUMMARY")
        print("-" * 20)
        print(f"🤖 Agent ID: {result.agent_id}")
        print(f"🏁 Finish Reason: {result.finish_reason}")
        print(f"😊 Overall Sentiment: {result.overall_sentiment}")
        print(f"📈 Total Interactions: {len(result.interactions)}")
        print(f"🐛 Bugs Encountered: {result.bugs_encountered}")
        
        if result.dropoff_reason:
            print(f"⚠️  Dropoff Reason: {result.dropoff_reason}")
        
        # Show interaction progression
        print(f"\n📋 INTERACTION SUMMARY")
        print("-" * 22)
        for interaction in result.interactions:
            step_emoji = "✅" if "success" in interaction.result.lower() else "❌" if "error" in interaction.result.lower() else "🔄"
            print(f"Step {interaction.step}: {step_emoji} {interaction.action_type} - {interaction.intent[:80]}...")
            print(f"         Result: {interaction.result[:100]}...")
            print(f"         Sentiment: {interaction.sentiment}")
            print()
        
        # Get agent insights from manager
        agent_info = agent_manager.get_agent(result.agent_id)
        if agent_info:
            print(f"\n🔬 DETAILED INSIGHTS")
            print("-" * 19)
            if agent_info.get('actual_url'):
                print(f"🌐 Actual URL Reached: {agent_info['actual_url']}")
            if agent_info.get('success_rate') is not None:
                print(f"🎯 Success Rate: {agent_info['success_rate']*100:.1f}%")
            if agent_info.get('action_breakdown'):
                actions = agent_info['action_breakdown']
                action_summary = ", ".join([f"{action}({count})" for action, count in actions.items()])
                print(f"🎬 Action Breakdown: {action_summary}")
            if agent_info.get('sentiment_progression'):
                print(f"📈 Sentiment Journey: {agent_info['sentiment_progression']}")
            if agent_info.get('session_duration_seconds'):
                duration = agent_info['session_duration_seconds']
                print(f"⏱️  Session Duration: {duration:.1f} seconds")
        
        # Show transcript location
        print(f"\n💾 DATA SAVED")
        print("-" * 11)
        print(f"📁 Agent Registry: data/agent_registry.json")
        print(f"📄 Transcript: data/{agent_input.run_id}/{result.agent_id}_transcript.json")
        print(f"🔍 Normalized: data/transcripts/{result.agent_id}_normalized.json")
        
        # Suggestions for next steps
        print(f"\n💡 NEXT STEPS")
        print("-" * 12)
        print("1. Review the transcript to see how the agent navigated")
        print("2. Check screenshots in the run directory")
        print("3. Use insights to optimize the user experience")
        print("4. Run additional agents with different personas")
        
        # Show how to query this agent later
        print(f"\n🔍 QUERY THIS AGENT LATER")
        print("-" * 25)
        print("# Find this specific run:")
        print(f"python -c \"")
        print(f"from services.agent_manager import AgentManager")
        print(f"manager = AgentManager()")
        print(f"agent = manager.get_agent('{result.agent_id}')")
        print(f"print('Agent Status:', agent['status'])")
        print(f"print('Success Rate:', agent.get('success_rate', 'N/A'))")
        print(f"\"")
        
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        return None
    
    return result


async def create_multiple_arcade_agents():
    """Create multiple agents with different personas to test various scenarios"""
    
    print("\n\n🎭 Creating Multiple Agents for Comprehensive Testing")
    print("=" * 55)
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY in .env file")
        return
    
    # Different personas for testing
    personas = [
        {
            "name": "Alex",
            "bio": (
                "Alex is a 28-year-old tech entrepreneur who wants to create a line of "
                "custom phone cases using AI. He's very comfortable with technology and "
                "expects intuitive, fast interfaces. Alex is impatient with slow loading "
                "times and gets frustrated with complex navigation."
            ),
            "scenario": "tech_entrepreneur_phone_cases"
        },
        {
            "name": "Sarah",
            "bio": (
                "Sarah is a 45-year-old traditional artist transitioning to digital creation. "
                "She's excited about AI but needs clear, step-by-step guidance. Sarah prefers "
                "visual interfaces and gets overwhelmed by too many options at once."
            ),
            "scenario": "traditional_artist_digital_transition"
        },
        {
            "name": "Carlos",
            "bio": (
                "Carlos is a 35-year-old small business owner who runs a local gift shop. "
                "He's heard about AI product creation but is skeptical about quality and "
                "cost. Carlos needs to understand the business value and pricing clearly."
            ),
            "scenario": "small_business_owner_cost_conscious"
        }
    ]
    
    results = []
    agent_manager = AgentManager(Path("data"))
    
    for i, persona_data in enumerate(personas, 1):
        print(f"\n🤖 Creating Agent {i}/3: {persona_data['name']}")
        print("-" * 30)
        
        persona = Persona(
            name=persona_data["name"],
            bio=persona_data["bio"]
        )
        
        agent_input = AgentInput(
            run_id=f"arcade_ai_test_{persona_data['scenario']}",
            url="https://www.arcade.ai/sell",
            persona=persona,
            ux_question=(
                f"As {persona_data['name']}, I want to explore Arcade's 'Create with AI' feature "
                "to understand if it's suitable for my business needs. Navigate to the Create with AI "
                "section and explore the interface. Focus on understanding the process, pricing, "
                "and capabilities. Stop once you've explored the main functionality."
            ),
            viewport=Viewport.DESKTOP,
            step_budget=12,
            max_consecutive_errors=3
        )
        
        try:
            agent = UXAgent(api_key, agent_manager=agent_manager)
            result = await agent.run(agent_input)
            results.append(result)
            
            print(f"✅ {persona_data['name']}: {result.finish_reason} ({result.overall_sentiment})")
            
        except Exception as e:
            print(f"❌ Error with {persona_data['name']}: {e}")
    
    # Summary of all agents
    if results:
        print(f"\n📊 MULTI-AGENT SUMMARY")
        print("-" * 22)
        
        successful = [r for r in results if r.finish_reason == "success"]
        print(f"✅ Successful: {len(successful)}/{len(results)}")
        
        sentiments = [r.overall_sentiment for r in results]
        print(f"😊 Sentiments: {', '.join(sentiments)}")
        
        total_interactions = sum([len(r.interactions) for r in results])
        print(f"🔄 Total Interactions: {total_interactions}")
        
        # Show how to analyze all agents together
        print(f"\n🔍 ANALYZE ALL AGENTS")
        print("-" * 20)
        print("python -c \"")
        print("from services.agent_manager import AgentManager")
        print("manager = AgentManager()")
        print("arcade_agents = manager.query_agents_by_insights(actual_url='https://www.arcade.ai/sell')")
        print("print(f'Found {len(arcade_agents)} Arcade agents')")
        print("summary = manager.get_performance_summary()")
        print("print('Performance:', summary)")
        print("\"")


if __name__ == "__main__":
    print("🎨 Arcade.ai Agent Creation Demo")
    print("================================")
    
    # Run single agent first
    result = asyncio.run(create_arcade_ai_agent())
    
    if result:
        # Ask if user wants to run multiple agents
        print(f"\n❓ Would you like to create multiple agents for comprehensive testing?")
        print("   This will create 3 different personas to test various user scenarios.")
        
        # For demo purposes, we'll run them automatically
        # In practice, you might want user input here
        print("🚀 Running multi-agent testing...")
        asyncio.run(create_multiple_arcade_agents())
    
    print("\n✨ Agent creation complete! Check the data directory for results.")
