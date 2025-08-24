"""
Dynamic Agent Management System

This module provides centralized agent tracking and transcription ingestion capabilities.
It decouples agent creation from hardcoded implementations and maintains a registry of all agents.
"""

import json
import uuid
import aiofiles
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class AgentManager:
    """
    Centralized agent management system that handles:
    - Dynamic agent creation and tracking
    - Unique agent ID generation
    - Transcript ingestion and normalization
    - Agent lifecycle management
    """
    
    def __init__(self, data_dir: Path = None):
        # Store data in venv directory instead of project directory
        if data_dir is None:
            # Find the venv directory
            import sys
            venv_path = Path(sys.executable).parent.parent  # From venv/bin/python to venv/
            self.data_dir = venv_path / "agent_data"
        else:
            self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory agent registry - simple dict structure
        self._agents: Dict[str, Dict[str, Any]] = {}
        
        # Transcript storage
        self.transcripts_dir = self.data_dir / "transcripts"
        self.transcripts_dir.mkdir(exist_ok=True)
        
        # Agent registry file
        self.registry_file = self.data_dir / "agent_registry.json"
        
        # Load existing registry if it exists
        self._load_registry()
    
    def generate_agent_id(self) -> str:
        """Generate a unique agent ID"""
        return f"agent_{uuid.uuid4().hex[:6]}"
    
    def create_agent(
        self,
        run_id: str,
        persona_name: str,
        persona_bio: str,
        url: str,
        ux_question: str
    ) -> str:
        """
        Create a new agent and return its unique agent_id
        
        Args:
            run_id: The run identifier
            persona_name: Name of the persona
            persona_bio: Biography/description of the persona
            url: Target URL for the agent
            ux_question: UX question the agent should answer
            
        Returns:
            str: Unique agent_id
        """
        agent_id = self.generate_agent_id()
        
        agent_info = {
            "agent_id": agent_id,
            "run_id": run_id,
            "persona_name": persona_name,
            "persona_bio": persona_bio,
            "url": url,
            "ux_question": ux_question,
            "status": "created",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "transcript_path": None,
            "transcript_source": None
        }
        
        # Add to registry
        self._agents[agent_id] = agent_info
        
        # Save registry
        self._save_registry()
        
        return agent_id
    
    def update_agent_status(self, agent_id: str, status: str) -> bool:
        """Update agent status"""
        if agent_id not in self._agents:
            return False
        
        self._agents[agent_id]["status"] = status
        self._agents[agent_id]["updated_at"] = datetime.utcnow().isoformat()
        self._save_registry()
        return True
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information by ID"""
        return self._agents.get(agent_id)
    
    def list_all_agents(self) -> List[Dict[str, Any]]:
        """List all tracked agents"""
        return list(self._agents.values())
    
    def list_agents_by_run(self, run_id: str) -> List[Dict[str, Any]]:
        """List agents for a specific run"""
        return [agent for agent in self._agents.values() if agent["run_id"] == run_id]
    
    def list_agents_by_status(self, status: str) -> List[Dict[str, Any]]:
        """List agents by status"""
        return [agent for agent in self._agents.values() if agent["status"] == status]
    
    def get_agent_ids(self) -> List[str]:
        """Get list of all agent IDs"""
        return list(self._agents.keys())
    
    def query_agents_by_insights(self, **filters) -> List[Dict[str, Any]]:
        """
        Query agents based on insights and performance metrics
        
        Args:
            **filters: Filtering criteria such as:
                - finish_reason: Filter by completion reason
                - overall_sentiment: Filter by overall sentiment
                - min_success_rate: Minimum success rate (0.0-1.0)
                - max_error_rate: Maximum error rate (0.0-1.0)
                - has_bugs: True/False for agents with bugs
                - user_dropped_off: True/False for dropoff cases
                - task_successful: True/False for successful completions
                - device_type: Filter by device type
                - min_steps: Minimum number of steps
                - max_steps: Maximum number of steps
        
        Returns:
            List of agents matching the criteria
        """
        matching_agents = []
        
        for agent in self._agents.values():
            matches = True
            
            # Check each filter
            for key, value in filters.items():
                if key == "min_success_rate":
                    if agent.get("success_rate", 0) < value:
                        matches = False
                        break
                elif key == "max_error_rate":
                    if agent.get("error_rate", 1) > value:
                        matches = False
                        break
                elif key == "has_bugs":
                    has_bugs = agent.get("bugs_encountered", 0) > 0
                    if has_bugs != value:
                        matches = False
                        break
                elif key == "min_steps":
                    if agent.get("total_steps", 0) < value:
                        matches = False
                        break
                elif key == "max_steps":
                    if agent.get("total_steps", 0) > value:
                        matches = False
                        break
                else:
                    # Direct value comparison
                    if agent.get(key) != value:
                        matches = False
                        break
            
            if matches:
                matching_agents.append(agent)
        
        return matching_agents
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all agents"""
        agents_with_insights = [a for a in self._agents.values() if a.get("finish_reason")]
        
        if not agents_with_insights:
            return {"message": "No agents with performance data found"}
        
        # Success rates
        success_rates = [a.get("success_rate", 0) for a in agents_with_insights if a.get("success_rate") is not None]
        error_rates = [a.get("error_rate", 0) for a in agents_with_insights if a.get("error_rate") is not None]
        
        # Completion analysis
        completion_types = {}
        sentiment_distribution = {}
        device_breakdown = {}
        
        for agent in agents_with_insights:
            # Completion types
            completion = agent.get("completion_type", "unknown")
            completion_types[completion] = completion_types.get(completion, 0) + 1
            
            # Sentiment distribution
            sentiment = agent.get("overall_sentiment", "neutral")
            sentiment_distribution[sentiment] = sentiment_distribution.get(sentiment, 0) + 1
            
            # Device breakdown
            device = agent.get("device_type", "unknown")
            device_breakdown[device] = device_breakdown.get(device, 0) + 1
        
        return {
            "total_agents_analyzed": len(agents_with_insights),
            "success_metrics": {
                "avg_success_rate": round(sum(success_rates) / len(success_rates), 2) if success_rates else 0,
                "avg_error_rate": round(sum(error_rates) / len(error_rates), 2) if error_rates else 0,
                "successful_completions": len([a for a in agents_with_insights if a.get("task_successful")]),
                "user_dropoffs": len([a for a in agents_with_insights if a.get("user_dropped_off")])
            },
            "completion_breakdown": completion_types,
            "sentiment_distribution": sentiment_distribution,
            "device_breakdown": device_breakdown,
            "bug_analysis": {
                "agents_with_bugs": len([a for a in agents_with_insights if a.get("bugs_encountered", 0) > 0]),
                "total_bugs": sum([a.get("bugs_encountered", 0) for a in agents_with_insights])
            }
        }
    
    async def ingest_transcript_file(
        self,
        filepath: Path,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Ingest a _transcript.json file and normalize it
        
        Args:
            filepath: Path to the transcript file
            agent_id: Optional agent_id to associate with (if None, extracted from file)
            run_id: Optional run_id to associate with (if None, extracted from file or generated)
            
        Returns:
            Tuple of (agent_id, normalized_transcript)
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Transcript file not found: {filepath}")
        
        # Load the transcript file
        async with aiofiles.open(filepath, 'r') as f:
            content = await f.read()
            raw_transcript = json.loads(content)
        
        # Extract or generate agent_id
        if agent_id is None:
            agent_id = raw_transcript.get('agent_id', self.generate_agent_id())
        
        # Extract or generate run_id
        if run_id is None:
            run_id = raw_transcript.get('run_id', str(uuid.uuid4()))
        
        # Normalize the transcript
        normalized = self._normalize_transcript(raw_transcript, agent_id, run_id, "ingested")
        
        # Save normalized transcript
        await self._save_normalized_transcript(normalized)
        
        # Extract insights from transcript
        insights = self._extract_insights(raw_transcript, normalized)
        
        # Update agent registry if agent exists
        if agent_id in self._agents:
            self._agents[agent_id]["transcript_path"] = str(filepath)
            self._agents[agent_id]["transcript_source"] = "ingested"
            self._agents[agent_id]["updated_at"] = datetime.utcnow().isoformat()
            # Add insights to existing agent
            self._agents[agent_id].update(insights)
        else:
            # Create new agent entry for ingested transcript
            persona = raw_transcript.get('persona', {})
            session = raw_transcript.get('session', {})
            
            agent_info = {
                "agent_id": agent_id,
                "run_id": run_id,
                "persona_name": persona.get('name', 'Unknown'),
                "persona_bio": persona.get('bio', 'No biography available'),
                "url": session.get('url', 'Unknown'),
                "ux_question": "Extracted from ingested transcript",
                "status": "ingested",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "transcript_path": str(filepath),
                "transcript_source": "ingested"
            }
            # Add insights to new agent
            agent_info.update(insights)
            self._agents[agent_id] = agent_info
        
        self._save_registry()
        return agent_id, normalized
    
    async def associate_transcript_with_agent(
        self,
        agent_id: str,
        transcript_data: Dict[str, Any],
        source: str = "agent_output"
    ) -> Dict[str, Any]:
        """
        Associate a transcript with an existing agent
        
        Args:
            agent_id: The agent ID
            transcript_data: Raw transcript data
            source: Source of the transcript
            
        Returns:
            Dict: Normalized transcript
        """
        if agent_id not in self._agents:
            raise ValueError(f"Agent {agent_id} not found in registry")
        
        agent_info = self._agents[agent_id]
        
        # Normalize the transcript
        normalized = self._normalize_transcript(
            transcript_data, 
            agent_id, 
            agent_info["run_id"], 
            source
        )
        
        # Save normalized transcript
        await self._save_normalized_transcript(normalized)
        
        # Extract insights from transcript and update agent
        insights = self._extract_insights(transcript_data, normalized)
        agent_info.update(insights)
        
        # Update agent info
        agent_info["transcript_source"] = source
        agent_info["updated_at"] = datetime.utcnow().isoformat()
        self._save_registry()
        
        return normalized
    
    async def get_normalized_transcript(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get normalized transcript for an agent"""
        transcript_file = self.transcripts_dir / f"{agent_id}_normalized.json"
        
        if not transcript_file.exists():
            return None
        
        async with aiofiles.open(transcript_file, 'r') as f:
            content = await f.read()
            data = json.loads(content)
            
        return data
    
    def _normalize_transcript(
        self,
        raw_transcript: Dict[str, Any],
        agent_id: str,
        run_id: str,
        source: str
    ) -> Dict[str, Any]:
        """
        Normalize a raw transcript into a consistent structure
        
        Args:
            raw_transcript: Raw transcript data
            agent_id: Agent identifier
            run_id: Run identifier
            source: Source of the transcript
            
        Returns:
            Dict: Normalized transcript
        """
        # Extract persona information
        persona = raw_transcript.get('persona', {})
        if isinstance(persona, dict):
            normalized_persona = {
                'name': persona.get('name', 'Unknown'),
                'bio': persona.get('bio', 'No biography available')
            }
        else:
            normalized_persona = {
                'name': 'Unknown',
                'bio': str(persona) if persona else 'No biography available'
            }
        
        # Extract interactions
        interactions = raw_transcript.get('interactions', [])
        normalized_interactions = []
        
        for interaction in interactions:
            normalized_interaction = {
                'step': interaction.get('step', 0),
                'timestamp': interaction.get('ts', interaction.get('timestamp', datetime.utcnow().isoformat())),
                'intent': interaction.get('intent', ''),
                'action_type': interaction.get('action_type', ''),
                'selector': interaction.get('selector'),
                'value': interaction.get('value'),
                'result': interaction.get('result', ''),
                'thought': interaction.get('thought', ''),
                'screenshot': interaction.get('screenshot'),
                'bug_detected': interaction.get('bug_detected', False),
                'bug_type': interaction.get('bug_type'),
                'bug_description': interaction.get('bug_description'),
                'sentiment': interaction.get('sentiment', 'neutral'),
                'user_feeling': interaction.get('user_feeling')
            }
            normalized_interactions.append(normalized_interaction)
        
        # Extract metadata
        session = raw_transcript.get('session', {})
        metadata = {
            'original_agent_id': raw_transcript.get('agent_id'),
            'session_url': session.get('url'),
            'device': session.get('device', 'unknown'),
            'browser': session.get('browser', 'unknown'),
            'finish_reason': raw_transcript.get('finish_reason'),
            'overall_sentiment': raw_transcript.get('overall_sentiment'),
            'bugs_encountered': raw_transcript.get('bugs_encountered', 0),
            'dropoff_reason': raw_transcript.get('dropoff_reason'),
            'total_interactions': len(normalized_interactions)
        }
        
        return {
            "agent_id": agent_id,
            "run_id": run_id,
            "persona": normalized_persona,
            "interactions": normalized_interactions,
            "metadata": metadata,
            "source": source,
            "ingested_at": datetime.utcnow().isoformat()
        }
    
    def _extract_insights(self, raw_transcript: Dict[str, Any], normalized: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract valuable insights from the transcript for agent tracking
        
        Args:
            raw_transcript: Original transcript data
            normalized: Normalized transcript data
            
        Returns:
            Dict: Insights to be added to agent info
        """
        insights = {}
        
        # Basic run information
        insights["finish_reason"] = raw_transcript.get("finish_reason")
        insights["overall_sentiment"] = raw_transcript.get("overall_sentiment")
        insights["bugs_encountered"] = raw_transcript.get("bugs_encountered", 0)
        insights["dropoff_reason"] = raw_transcript.get("dropoff_reason")
        
        # Session information
        session = raw_transcript.get("session", {})
        insights["actual_url"] = session.get("url")
        insights["device_type"] = session.get("device", "unknown")
        insights["browser"] = session.get("browser", "chromium")
        
        # Interaction analysis
        interactions = normalized.get("interactions", [])
        insights["total_steps"] = len(interactions)
        
        if interactions:
            # Sentiment progression
            sentiments = [i.get("sentiment", "neutral") for i in interactions]
            insights["sentiment_progression"] = " -> ".join(sentiments)
            insights["final_sentiment"] = sentiments[-1] if sentiments else "neutral"
            
            # Action type analysis
            action_types = [i.get("action_type", "") for i in interactions]
            action_counts = {}
            for action in action_types:
                if action:
                    action_counts[action] = action_counts.get(action, 0) + 1
            insights["action_breakdown"] = action_counts
            
            # Bug analysis
            bugs = [i for i in interactions if i.get("bug_detected")]
            insights["bug_steps"] = [i.get("step") for i in bugs]
            insights["bug_types"] = list(set([i.get("bug_type") for i in bugs if i.get("bug_type")]))
            
            # Performance metrics
            insights["success_rate"] = self._calculate_success_rate(interactions)
            insights["error_rate"] = self._calculate_error_rate(interactions)
            
            # User experience insights
            insights["frustration_points"] = self._identify_frustration_points(interactions)
            insights["positive_moments"] = self._identify_positive_moments(interactions)
        
        # Completion insights
        if insights["finish_reason"]:
            insights["completion_type"] = self._categorize_completion(insights["finish_reason"])
            insights["user_dropped_off"] = insights["finish_reason"] == "user_dropoff"
            insights["task_successful"] = insights["finish_reason"] == "success"
        
        # Duration (if available)
        if interactions and len(interactions) > 1:
            first_time = interactions[0].get("timestamp")
            last_time = interactions[-1].get("timestamp")
            if first_time and last_time:
                try:
                    first_dt = datetime.fromisoformat(first_time.replace('Z', '+00:00'))
                    last_dt = datetime.fromisoformat(last_time.replace('Z', '+00:00'))
                    duration = (last_dt - first_dt).total_seconds()
                    insights["session_duration_seconds"] = duration
                    insights["avg_time_per_step"] = duration / len(interactions) if len(interactions) > 1 else 0
                except:
                    pass
        
        return insights
    
    def _calculate_success_rate(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate the success rate of actions"""
        if not interactions:
            return 0.0
        
        successful_actions = 0
        for interaction in interactions:
            result = interaction.get("result", "").lower()
            if any(success_word in result for success_word in ["clicked", "filled", "navigated", "scrolled", "success"]):
                successful_actions += 1
        
        return round(successful_actions / len(interactions), 2)
    
    def _calculate_error_rate(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate the error rate of actions"""
        if not interactions:
            return 0.0
        
        error_actions = 0
        for interaction in interactions:
            result = interaction.get("result", "").lower()
            bug_detected = interaction.get("bug_detected", False)
            if bug_detected or any(error_word in result for error_word in ["error", "failed", "timeout", "not_found"]):
                error_actions += 1
        
        return round(error_actions / len(interactions), 2)
    
    def _identify_frustration_points(self, interactions: List[Dict[str, Any]]) -> List[int]:
        """Identify steps where the user became frustrated"""
        frustration_steps = []
        
        for interaction in interactions:
            sentiment = interaction.get("sentiment", "neutral")
            if sentiment in ["frustrated", "negative"]:
                frustration_steps.append(interaction.get("step", 0))
        
        return frustration_steps
    
    def _identify_positive_moments(self, interactions: List[Dict[str, Any]]) -> List[int]:
        """Identify steps where the user had positive experiences"""
        positive_steps = []
        
        for interaction in interactions:
            sentiment = interaction.get("sentiment", "neutral")
            if sentiment in ["positive", "very_positive"]:
                positive_steps.append(interaction.get("step", 0))
        
        return positive_steps
    
    def _categorize_completion(self, finish_reason: str) -> str:
        """Categorize the type of completion"""
        completion_map = {
            "success": "successful_completion",
            "user_dropoff": "user_abandoned",
            "step_budget_reached": "timeout_reached",
            "consecutive_errors": "technical_failure",
            "nav_failure": "navigation_failure"
        }
        return completion_map.get(finish_reason, "unknown_completion")
    
    async def _save_normalized_transcript(self, transcript: Dict[str, Any]) -> None:
        """Save a normalized transcript to disk"""
        filepath = self.transcripts_dir / f"{transcript['agent_id']}_normalized.json"
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(transcript, indent=2, default=str))
    
    def _load_registry(self) -> None:
        """Load agent registry from disk"""
        if not self.registry_file.exists():
            return
        
        try:
            with open(self.registry_file, 'r') as f:
                self._agents = json.load(f)
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Could not load agent registry: {e}")
            self._agents = {}
    
    def _save_registry(self) -> None:
        """Save agent registry to disk"""
        with open(self.registry_file, 'w') as f:
            json.dump(self._agents, f, indent=2, default=str)
    
    async def cleanup_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from tracking and optionally clean up its files
        
        Args:
            agent_id: Agent to remove
            
        Returns:
            bool: True if agent was removed, False if not found
        """
        if agent_id not in self._agents:
            return False
        
        # Remove from registry
        del self._agents[agent_id]
        
        # Save updated registry
        self._save_registry()
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about tracked agents"""
        total_agents = len(self._agents)
        status_counts = {}
        run_counts = {}
        
        for agent in self._agents.values():
            # Count by status
            status_counts[agent["status"]] = status_counts.get(agent["status"], 0) + 1
            
            # Count by run
            run_counts[agent["run_id"]] = run_counts.get(agent["run_id"], 0) + 1
        
        return {
            'total_agents': total_agents,
            'status_breakdown': status_counts,
            'runs_with_agents': len(run_counts),
            'agents_per_run': run_counts,
            'agents_with_transcripts': len([a for a in self._agents.values() if a.get("transcript_path")])
        }
