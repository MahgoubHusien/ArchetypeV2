#!/usr/bin/env python3
"""
Demo script for the Dynamic Agent Management System

This script demonstrates:
1. Creating agents dynamically with unique IDs
2. Tracking agent lifecycle
3. Ingesting existing transcript files
4. Normalizing transcript structures
5. Querying agent information
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from services.agent_manager import AgentManager
from models.schemas import AgentInput, Persona, Viewport

load_dotenv()


async def demo_agent_tracking():
    """Demonstrate dynamic agent tracking capabilities"""
    
    print("🤖 Dynamic Agent Management System Demo")
    print("=" * 50)
    
    # Initialize the agent manager
    data_dir = Path("data")
    agent_manager = AgentManager(data_dir)
    
    print(f"\n📁 Using data directory: {data_dir}")
    
    # Demo 1: Create multiple agents dynamically
    print("\n🚀 Demo 1: Creating Dynamic Agents")
    print("-" * 30)
    
    agents_to_create = [
        {
            "run_id": "demo_run_001",
            "persona_name": "Alice",
            "persona_bio": "Alice is a 28-year-old UX researcher who loves testing new interfaces",
            "url": "https://example.com",
            "ux_question": "How easy is it to find the contact information?"
        },
        {
            "run_id": "demo_run_001", 
            "persona_name": "Bob",
            "persona_bio": "Bob is a 45-year-old executive who values efficiency and clarity",
            "url": "https://example.com",
            "ux_question": "Can I quickly understand what this company does?"
        },
        {
            "run_id": "demo_run_002",
            "persona_name": "Charlie",
            "persona_bio": "Charlie is a 19-year-old student comfortable with modern web interfaces",
            "url": "https://shop.example.com",
            "ux_question": "How easy is it to find and purchase a product?"
        }
    ]
    
    created_agents = []
    for agent_data in agents_to_create:
        agent_id = agent_manager.create_agent(**agent_data)
        created_agents.append(agent_id)
        print(f"✅ Created agent: {agent_id} (Persona: {agent_data['persona_name']})")
    
    # Demo 2: List all agents
    print(f"\n📋 Demo 2: Agent Registry")
    print("-" * 20)
    
    all_agents = agent_manager.list_all_agents()
    print(f"Total agents tracked: {len(all_agents)}")
    
    for agent in all_agents:
        print(f"  🤖 {agent['agent_id']}")
        print(f"     Persona: {agent['persona_name']}")
        print(f"     Run: {agent['run_id']}")
        print(f"     Status: {agent['status']}")
        print(f"     Created: {agent['created_at']}")
        print()
    
    # Demo 3: Update agent statuses
    print("\n🔄 Demo 3: Updating Agent Status")
    print("-" * 30)
    
    if created_agents:
        agent_id = created_agents[0]
        agent_manager.update_agent_status(agent_id, "running")
        print(f"✅ Updated {agent_id} status to 'running'")
        
        agent_manager.update_agent_status(agent_id, "completed") 
        print(f"✅ Updated {agent_id} status to 'completed'")
    
    # Demo 4: Query agents by run and status
    print("\n🔍 Demo 4: Querying Agents")
    print("-" * 25)
    
    # By run ID
    run_agents = agent_manager.list_agents_by_run("demo_run_001")
    print(f"Agents in 'demo_run_001': {len(run_agents)}")
    for agent in run_agents:
        print(f"  - {agent['agent_id']} ({agent['persona_name']})")
    
    # By status
    completed_agents = agent_manager.list_agents_by_status("completed")
    print(f"\nCompleted agents: {len(completed_agents)}")
    for agent in completed_agents:
        print(f"  - {agent['agent_id']} ({agent['persona_name']})")
    
    # Demo 5: Ingest existing transcript files
    print("\n📥 Demo 5: Transcript Ingestion")
    print("-" * 30)
    
    # Find existing transcript files
    transcript_files = list(data_dir.glob("*/*_transcript.json"))
    print(f"Found {len(transcript_files)} existing transcript files")
    
    ingested_count = 0
    for filepath in transcript_files[:3]:  # Limit to first 3 for demo
        try:
            agent_id, normalized_transcript = await agent_manager.ingest_transcript_file(filepath)
            print(f"✅ Ingested transcript: {filepath.name} -> Agent {agent_id}")
            print(f"   Persona: {normalized_transcript['persona']['name']}")
            print(f"   Interactions: {len(normalized_transcript['interactions'])}")
            print(f"   Source: {normalized_transcript['source']}")
            ingested_count += 1
        except Exception as e:
            print(f"❌ Failed to ingest {filepath.name}: {e}")
    
    print(f"\n📊 Successfully ingested {ingested_count} transcripts")
    
    # Demo 6: Get agent statistics
    print("\n📈 Demo 6: Agent Statistics")
    print("-" * 25)
    
    stats = agent_manager.get_stats()
    print(f"Total agents: {stats['total_agents']}")
    print(f"Runs with agents: {stats['runs_with_agents']}")
    print(f"Agents with transcripts: {stats['agents_with_transcripts']}")
    
    print("\nStatus breakdown:")
    for status, count in stats['status_breakdown'].items():
        print(f"  {status}: {count}")
    
    print("\nAgents per run:")
    for run_id, count in stats['agents_per_run'].items():
        print(f"  {run_id}: {count}")
    
    # Demo 7: Get specific agent details
    print("\n🔍 Demo 7: Agent Details")
    print("-" * 22)
    
    if created_agents:
        agent_id = created_agents[0]
        agent_info = agent_manager.get_agent(agent_id)
        if agent_info:
            print(f"Agent: {agent_info['agent_id']}")
            print(f"  Run ID: {agent_info['run_id']}")
            print(f"  Persona: {agent_info['persona_name']}")
            print(f"  Bio: {agent_info['persona_bio'][:100]}...")
            print(f"  URL: {agent_info['url']}")
            print(f"  Question: {agent_info['ux_question'][:80]}...")
            print(f"  Status: {agent_info['status']}")
            print(f"  Created: {agent_info['created_at']}")
            print(f"  Updated: {agent_info['updated_at']}")
            
            if agent_info.get('transcript_path'):
                print(f"  Transcript: {agent_info['transcript_path']}")
                print(f"  Source: {agent_info['transcript_source']}")
    
    print("\n🎉 Demo completed! Agent management system is working correctly.")
    print(f"💾 Registry saved to: {agent_manager.registry_file}")


async def demo_transcript_normalization():
    """Demonstrate transcript normalization"""
    print("\n🔄 Transcript Normalization Demo")
    print("=" * 35)
    
    agent_manager = AgentManager(Path("data"))
    
    # Find a transcript file to demonstrate normalization
    transcript_files = list(Path("data").glob("*/*_transcript.json"))
    
    if not transcript_files:
        print("❌ No transcript files found for demonstration")
        return
    
    filepath = transcript_files[0]
    print(f"📄 Using transcript file: {filepath}")
    
    try:
        # Ingest and normalize
        agent_id, normalized = await agent_manager.ingest_transcript_file(filepath)
        
        print(f"\n✅ Normalized transcript for agent: {agent_id}")
        print(f"   Original agent ID: {normalized['metadata'].get('original_agent_id')}")
        print(f"   Persona: {normalized['persona']['name']}")
        print(f"   Total interactions: {len(normalized['interactions'])}")
        print(f"   Session URL: {normalized['metadata'].get('session_url')}")
        print(f"   Device: {normalized['metadata'].get('device')}")
        print(f"   Browser: {normalized['metadata'].get('browser')}")
        print(f"   Finish reason: {normalized['metadata'].get('finish_reason')}")
        print(f"   Overall sentiment: {normalized['metadata'].get('overall_sentiment')}")
        print(f"   Bugs encountered: {normalized['metadata'].get('bugs_encountered')}")
        print(f"   Ingested at: {normalized['ingested_at']}")
        
        # Show sample interactions
        print(f"\n📋 Sample interactions:")
        for i, interaction in enumerate(normalized['interactions'][:3]):
            print(f"   Step {interaction['step']}: {interaction['action_type']}")
            print(f"     Intent: {interaction['intent'][:60]}...")
            print(f"     Result: {interaction['result'][:60]}...")
            print(f"     Sentiment: {interaction['sentiment']}")
            print()
        
        # Retrieve the normalized transcript
        retrieved = await agent_manager.get_normalized_transcript(agent_id)
        if retrieved:
            print(f"✅ Successfully retrieved normalized transcript for {agent_id}")
        else:
            print(f"❌ Could not retrieve normalized transcript for {agent_id}")
            
    except Exception as e:
        print(f"❌ Error during normalization: {e}")


if __name__ == "__main__":
    print("🚀 Starting Dynamic Agent Management Demo")
    
    # Run both demos
    asyncio.run(demo_agent_tracking())
    asyncio.run(demo_transcript_normalization())
    
    print("\n✨ All demos completed successfully!")
