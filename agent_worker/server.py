import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from agent import UXAgent
from models.schemas import AgentInput, AgentOutput, Persona, Viewport
from utils.storage import TranscriptStorage

load_dotenv()

app = FastAPI(title="Agent Worker API")

# Add CORS middleware for Vercel frontend and Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://test-persona-hub.vercel.app",  # Your Vercel frontend
        "https://preview--test-persona-hub.lovable.app",
        "https://lovable.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "https://*.onrender.com",  # Allow all Render domains
        "https://archetype-backend.onrender.com",
        "https://archetype-agent-worker.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for screenshots
app.mount("/static", StaticFiles(directory="static"), name="static")

# Storage instance
storage = TranscriptStorage()


class RunAgentRequest(BaseModel):
    run_id: str
    url: str
    persona: Persona
    ux_question: str
    viewport: str = "mobile"
    step_budget: int = 5
    max_consecutive_errors: int = 2
    seed: int = 7


@app.post("/agent/run")
async def run_agent(request: RunAgentRequest) -> AgentOutput:
    """Run a single agent."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    # Convert to AgentInput
    agent_input = AgentInput(
        run_id=request.run_id,
        url=request.url,
        persona=request.persona,
        ux_question=request.ux_question,
        viewport=Viewport(request.viewport),
        step_budget=request.step_budget,
        max_consecutive_errors=request.max_consecutive_errors,
        seed=request.seed
    )
    
    # Run agent
    agent = UXAgent(api_key)
    result = await agent.run(agent_input)
    
    # Save transcript
    await storage.save_transcript(request.run_id, result)
    
    return result


@app.get("/agent/transcript/{run_id}")
async def get_transcripts(run_id: str) -> List[dict]:
    """Get all agent transcripts for a run."""
    try:
        transcripts = await storage.list_transcripts(run_id)
        return transcripts
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Run not found")


@app.get("/health")
async def health():
    """Health check."""
    return {"ok": True, "service": "agent-worker"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)