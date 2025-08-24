#!/usr/bin/env python3
"""
Batch Transcript Ingestion Utility

This utility provides commands for batch ingesting _transcript.json files 
into the dynamic agent management system.
"""

import asyncio
import argparse
import json
from pathlib import Path
from typing import List, Tuple

from services.agent_manager import AgentManager


async def ingest_directory(
    agent_manager: AgentManager, 
    directory: Path, 
    recursive: bool = False
) -> Tuple[int, int]:
    """
    Ingest all transcript files from a directory
    
    Args:
        agent_manager: Agent manager instance
        directory: Directory to search for transcript files
        recursive: Whether to search recursively
        
    Returns:
        Tuple of (success_count, total_count)
    """
    # Find transcript files
    if recursive:
        pattern = "**/*_transcript.json"
    else:
        pattern = "*_transcript.json"
    
    transcript_files = list(directory.glob(pattern))
    
    print(f"Found {len(transcript_files)} transcript files in {directory}")
    
    success_count = 0
    
    for filepath in transcript_files:
        try:
            agent_id, normalized = await agent_manager.ingest_transcript_file(filepath)
            print(f"✅ Ingested: {filepath.relative_to(directory)} -> Agent {agent_id}")
            print(f"   Persona: {normalized.persona['name']}")
            print(f"   Interactions: {len(normalized.interactions)}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to ingest {filepath.relative_to(directory)}: {e}")
    
    return success_count, len(transcript_files)


async def ingest_file_list(
    agent_manager: AgentManager, 
    file_paths: List[Path]
) -> Tuple[int, int]:
    """
    Ingest specific transcript files
    
    Args:
        agent_manager: Agent manager instance
        file_paths: List of file paths to ingest
        
    Returns:
        Tuple of (success_count, total_count)
    """
    success_count = 0
    
    for filepath in file_paths:
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            continue
            
        try:
            agent_id, normalized = await agent_manager.ingest_transcript_file(filepath)
            print(f"✅ Ingested: {filepath.name} -> Agent {agent_id}")
            print(f"   Persona: {normalized.persona['name']}")
            print(f"   Interactions: {len(normalized.interactions)}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to ingest {filepath.name}: {e}")
    
    return success_count, len(file_paths)


async def validate_transcript_files(directory: Path, recursive: bool = False) -> None:
    """
    Validate transcript files without ingesting them
    
    Args:
        directory: Directory to search for transcript files
        recursive: Whether to search recursively
    """
    # Find transcript files
    if recursive:
        pattern = "**/*_transcript.json"
    else:
        pattern = "*_transcript.json"
    
    transcript_files = list(directory.glob(pattern))
    
    print(f"Validating {len(transcript_files)} transcript files...")
    
    valid_count = 0
    
    for filepath in transcript_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Check required fields
            required_fields = ['agent_id', 'persona', 'interactions']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ {filepath.name}: Missing fields: {missing_fields}")
            else:
                interactions = data.get('interactions', [])
                persona = data.get('persona', {})
                persona_name = persona.get('name', 'Unknown') if isinstance(persona, dict) else 'Unknown'
                
                print(f"✅ {filepath.name}: Valid ({len(interactions)} interactions, persona: {persona_name})")
                valid_count += 1
                
        except json.JSONDecodeError as e:
            print(f"❌ {filepath.name}: Invalid JSON - {e}")
        except Exception as e:
            print(f"❌ {filepath.name}: Error - {e}")
    
    print(f"\nValidation complete: {valid_count}/{len(transcript_files)} files are valid")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Batch transcript ingestion utility for dynamic agent management"
    )
    
    # Add subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest directory command
    ingest_dir_parser = subparsers.add_parser('ingest-dir', help='Ingest all transcripts from a directory')
    ingest_dir_parser.add_argument('directory', type=Path, help='Directory containing transcript files')
    ingest_dir_parser.add_argument('--recursive', '-r', action='store_true', help='Search recursively')
    ingest_dir_parser.add_argument('--data-dir', type=Path, default=Path('data'), help='Agent data directory')
    
    # Ingest files command  
    ingest_files_parser = subparsers.add_parser('ingest-files', help='Ingest specific transcript files')
    ingest_files_parser.add_argument('files', nargs='+', type=Path, help='Transcript files to ingest')
    ingest_files_parser.add_argument('--data-dir', type=Path, default=Path('data'), help='Agent data directory')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate transcript files without ingesting')
    validate_parser.add_argument('directory', type=Path, help='Directory containing transcript files')
    validate_parser.add_argument('--recursive', '-r', action='store_true', help='Search recursively')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show agent manager statistics')
    stats_parser.add_argument('--data-dir', type=Path, default=Path('data'), help='Agent data directory')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List tracked agents')
    list_parser.add_argument('--data-dir', type=Path, default=Path('data'), help='Agent data directory')
    list_parser.add_argument('--run-id', help='Filter by run ID')
    list_parser.add_argument('--status', help='Filter by status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    async def run_command():
        if args.command in ['ingest-dir', 'ingest-files', 'stats', 'list']:
            agent_manager = AgentManager(args.data_dir)
        
        if args.command == 'ingest-dir':
            print(f"Ingesting transcripts from: {args.directory}")
            if args.recursive:
                print("Searching recursively...")
            
            success_count, total_count = await ingest_directory(
                agent_manager, args.directory, args.recursive
            )
            
            print(f"\nIngestion complete: {success_count}/{total_count} files processed successfully")
            
        elif args.command == 'ingest-files':
            print(f"Ingesting {len(args.files)} transcript files...")
            
            success_count, total_count = await ingest_file_list(agent_manager, args.files)
            
            print(f"\nIngestion complete: {success_count}/{total_count} files processed successfully")
            
        elif args.command == 'validate':
            print(f"Validating transcripts in: {args.directory}")
            if args.recursive:
                print("Searching recursively...")
            
            await validate_transcript_files(args.directory, args.recursive)
            
        elif args.command == 'stats':
            stats = agent_manager.get_stats()
            
            print("📊 Agent Manager Statistics")
            print("=" * 30)
            print(f"Total agents: {stats['total_agents']}")
            print(f"Runs with agents: {stats['runs_with_agents']}")
            print(f"Agents with transcripts: {stats['agents_with_transcripts']}")
            
            print("\nStatus breakdown:")
            for status, count in stats['status_breakdown'].items():
                print(f"  {status}: {count}")
            
            print("\nTop runs by agent count:")
            sorted_runs = sorted(stats['agents_per_run'].items(), key=lambda x: x[1], reverse=True)
            for run_id, count in sorted_runs[:10]:
                print(f"  {run_id}: {count}")
                
        elif args.command == 'list':
            agents = agent_manager.list_all_agents()
            
            # Apply filters
            if args.run_id:
                agents = [a for a in agents if a['run_id'] == args.run_id]
            if args.status:
                agents = [a for a in agents if a['status'] == args.status]
            
            print(f"📋 Tracked Agents ({len(agents)} total)")
            print("=" * 50)
            
            for agent in agents:
                print(f"🤖 {agent['agent_id']}")
                print(f"   Run: {agent['run_id']}")
                print(f"   Persona: {agent['persona_name']}")
                print(f"   Status: {agent['status']}")
                print(f"   Created: {agent['created_at']}")
                if agent.get('transcript_path'):
                    print(f"   Transcript: {agent['transcript_path']}")
                print()
    
    # Run the async command
    asyncio.run(run_command())


if __name__ == "__main__":
    main()
