#!/usr/bin/env python3
"""
Agent Insights Dashboard

This script demonstrates the rich insights captured by the Agent Management System
"""

import asyncio
import json
from pathlib import Path
from services.agent_manager import AgentManager


async def show_detailed_insights():
    """Show detailed insights for all agents"""
    
    print("🔬 Agent Insights Dashboard")
    print("=" * 50)
    
    manager = AgentManager()
    
    # Performance Overview
    print("\n📊 PERFORMANCE OVERVIEW")
    print("-" * 25)
    summary = manager.get_performance_summary()
    
    if "message" in summary:
        print(summary["message"])
        return
    
    print(f"📈 Total Agents Analyzed: {summary['total_agents_analyzed']}")
    print(f"✅ Successful Completions: {summary['success_metrics']['successful_completions']}")
    print(f"❌ User Dropoffs: {summary['success_metrics']['user_dropoffs']}")
    print(f"🎯 Average Success Rate: {summary['success_metrics']['avg_success_rate']*100:.1f}%")
    print(f"⚠️  Average Error Rate: {summary['success_metrics']['avg_error_rate']*100:.1f}%")
    
    print("\n🏁 Completion Types:")
    for completion_type, count in summary['completion_breakdown'].items():
        print(f"  {completion_type}: {count}")
    
    print("\n😊 Sentiment Distribution:")
    for sentiment, count in summary['sentiment_distribution'].items():
        print(f"  {sentiment}: {count}")
    
    print("\n🖥️  Device Breakdown:")
    for device, count in summary['device_breakdown'].items():
        print(f"  {device}: {count}")
    
    print(f"\n🐛 Bug Analysis:")
    print(f"  Agents with bugs: {summary['bug_analysis']['agents_with_bugs']}")
    print(f"  Total bugs found: {summary['bug_analysis']['total_bugs']}")
    
    # Individual Agent Analysis
    print("\n🤖 INDIVIDUAL AGENT INSIGHTS")
    print("-" * 30)
    
    agents = manager.list_all_agents()
    agents_with_insights = [a for a in agents if a.get('finish_reason')]
    
    for i, agent in enumerate(agents_with_insights, 1):
        print(f"\n[{i}] {agent['agent_id']} - {agent['persona_name']}")
        print(f"    🌐 URL: {agent.get('actual_url', 'Unknown')}")
        print(f"    🎭 Persona: {agent['persona_bio'][:100]}...")
        print(f"    ❓ Question: {agent['ux_question'][:80]}...")
        print(f"    🏁 Finish Reason: {agent.get('finish_reason')}")
        print(f"    😊 Overall Sentiment: {agent.get('overall_sentiment')}")
        print(f"    ✅ Success Rate: {agent.get('success_rate', 0)*100:.1f}%")
        print(f"    ❌ Error Rate: {agent.get('error_rate', 0)*100:.1f}%")
        print(f"    📊 Total Steps: {agent.get('total_steps', 0)}")
        print(f"    🖥️  Device: {agent.get('device_type', 'unknown')}")
        print(f"    🐛 Bugs Encountered: {agent.get('bugs_encountered', 0)}")
        
        # Sentiment progression
        if agent.get('sentiment_progression'):
            print(f"    📈 Sentiment Journey: {agent['sentiment_progression']}")
        
        # Action breakdown
        if agent.get('action_breakdown'):
            actions = agent['action_breakdown']
            action_summary = ", ".join([f"{action}({count})" for action, count in actions.items()])
            print(f"    🎬 Actions: {action_summary}")
        
        # Timing information
        if agent.get('session_duration_seconds'):
            duration = agent['session_duration_seconds']
            avg_time = agent.get('avg_time_per_step', 0)
            print(f"    ⏱️  Duration: {duration:.1f}s (avg {avg_time:.1f}s/step)")
        
        # Frustration and positive moments
        frustration = agent.get('frustration_points', [])
        positive = agent.get('positive_moments', [])
        if frustration:
            print(f"    😤 Frustration Points: Steps {frustration}")
        if positive:
            print(f"    🎉 Positive Moments: Steps {positive}")
    
    # Query Examples
    print("\n🔍 QUERY EXAMPLES")
    print("-" * 17)
    
    # Find successful agents
    successful = manager.query_agents_by_insights(task_successful=True)
    print(f"\n✅ Successful Agents ({len(successful)}):")
    for agent in successful:
        print(f"  - {agent['agent_id']}: {agent.get('success_rate', 0)*100:.1f}% success rate")
    
    # Find agents with high success rate
    high_performers = manager.query_agents_by_insights(min_success_rate=0.8)
    print(f"\n🏆 High Performers (>80% success) ({len(high_performers)}):")
    for agent in high_performers:
        print(f"  - {agent['agent_id']}: {agent.get('success_rate', 0)*100:.1f}% success rate")
    
    # Find agents with bugs
    buggy = manager.query_agents_by_insights(has_bugs=True)
    print(f"\n🐛 Agents with Bugs ({len(buggy)}):")
    for agent in buggy:
        print(f"  - {agent['agent_id']}: {agent.get('bugs_encountered', 0)} bugs")
    
    # Find agents by sentiment
    positive_agents = manager.query_agents_by_insights(overall_sentiment='very_positive')
    print(f"\n😍 Very Positive Agents ({len(positive_agents)}):")
    for agent in positive_agents:
        print(f"  - {agent['agent_id']}: {agent.get('total_steps', 0)} steps")
    
    # Find long sessions
    long_sessions = manager.query_agents_by_insights(min_steps=5)
    print(f"\n⏳ Long Sessions (>5 steps) ({len(long_sessions)}):")
    for agent in long_sessions:
        print(f"  - {agent['agent_id']}: {agent.get('total_steps', 0)} steps")


async def show_raw_agent_data():
    """Show the raw agent data structure"""
    print("\n\n🗂️  RAW AGENT DATA STRUCTURE")
    print("=" * 35)
    
    manager = AgentManager()
    agents = manager.list_all_agents()
    
    if agents:
        # Show one agent as example
        example_agent = None
        for agent in agents:
            if agent.get('finish_reason'):
                example_agent = agent
                break
        
        if example_agent:
            print(f"\n📋 Example Agent Data ({example_agent['agent_id']}):")
            print("-" * 30)
            
            # Pretty print the agent data
            formatted_data = json.dumps(example_agent, indent=2, default=str)
            print(formatted_data)
        else:
            print("No agents with insights found")
    else:
        print("No agents found")


if __name__ == "__main__":
    print("🚀 Loading Agent Insights...")
    
    asyncio.run(show_detailed_insights())
    asyncio.run(show_raw_agent_data())
    
    print("\n✨ Insights dashboard complete!")
