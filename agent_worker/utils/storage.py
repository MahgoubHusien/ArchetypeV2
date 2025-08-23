import json
import aiofiles
from pathlib import Path
from typing import Any, Dict, List
try:
    from ..models.schemas import AgentOutput
except ImportError:
    from models.schemas import AgentOutput


class TranscriptStorage:
    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_transcript(self, run_id: str, agent_output: AgentOutput) -> Path:
        """Save agent transcript to JSON file."""
        run_dir = self.data_dir / run_id
        run_dir.mkdir(exist_ok=True)
        
        filepath = run_dir / f"{agent_output.agent_id}_transcript.json"
        
        # Convert to dict with proper serialization
        data = agent_output.model_dump(mode='json')
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(data, indent=2, default=str))
        
        return filepath
    
    async def load_transcript(self, run_id: str, agent_id: str) -> Dict[str, Any]:
        """Load agent transcript from JSON file."""
        filepath = self.data_dir / run_id / f"{agent_id}_transcript.json"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Transcript not found: {filepath}")
        
        async with aiofiles.open(filepath, 'r') as f:
            content = await f.read()
            return json.loads(content)
    
    async def list_transcripts(self, run_id: str) -> List[Dict[str, Any]]:
        """List all transcripts for a run."""
        run_dir = self.data_dir / run_id
        
        if not run_dir.exists():
            return []
        
        transcripts = []
        for filepath in run_dir.glob("*_transcript.json"):
            async with aiofiles.open(filepath, 'r') as f:
                content = await f.read()
                transcripts.append(json.loads(content))
        
        return transcripts