from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from uuid import UUID
import os
from supabase import create_client, Client

from data_models import Agent, Interaction, Run

# Import settings
from config import settings

# Validate settings
settings.validate_required_settings()

# Initialize FastAPI app
app = FastAPI(
    title="Agent API",
    description="API for managing agents, interactions, and runs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Agent API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "agent-api"}


# Agent endpoints
@app.get("/agents", response_model=List[Agent])
async def get_agents(supabase: Client = Depends(get_supabase)):
    """Get all agents"""
    try:
        response = supabase.table("agent").select("*").execute()
        return [Agent(**agent) for agent in response.data] if response.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get a specific agent by ID"""
    try:
        response = supabase.table("agent").select("*").eq("agent_id", str(agent_id)).execute()
        if response.data and len(response.data) > 0:
            return Agent(**response.data[0])
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/agents/by-run/{run_id}", response_model=List[Agent])
async def get_agents_by_run(run_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get all agents for a specific run ID"""
    try:
        response = supabase.table("agent").select("*").eq("run_id", str(run_id)).execute()
        return [Agent(**agent) for agent in response.data] if response.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Interaction endpoints
@app.get("/interactions", response_model=List[Interaction])
async def get_interactions(supabase: Client = Depends(get_supabase)):
    """Get all interactions"""
    try:
        response = supabase.table("interaction").select("*").execute()
        return [Interaction(**interaction) for interaction in response.data] if response.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/interactions/{interaction_id}", response_model=Interaction)
async def get_interaction(interaction_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get a specific interaction by ID"""
    try:
        response = supabase.table("interaction").select("*").eq("interaction_id", str(interaction_id)).execute()
        if response.data and len(response.data) > 0:
            return Interaction(**response.data[0])
        else:
            raise HTTPException(status_code=404, detail="Interaction not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/interactions/by-agent/{agent_id}", response_model=List[Interaction])
async def get_interactions_by_agent(agent_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get all interactions for a specific agent ID"""
    try:
        response = supabase.table("interaction").select("*").eq("agent_id", str(agent_id)).execute()
        return [Interaction(**interaction) for interaction in response.data] if response.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Run endpoints
@app.get("/runs", response_model=List[Run])
async def get_runs(supabase: Client = Depends(get_supabase)):
    """Get all runs"""
    try:
        response = supabase.table("run").select("*").execute()
        return [Run(**run) for run in response.data] if response.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/runs/{run_id}", response_model=Run)
async def get_run(run_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get a specific run by ID"""
    try:
        response = supabase.table("run").select("*").eq("run_id", str(run_id)).execute()
        if response.data and len(response.data) > 0:
            return Run(**response.data[0])
        else:
            raise HTTPException(status_code=404, detail="Run not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)