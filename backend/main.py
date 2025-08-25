from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from supabase import create_client, Client
import os
import asyncio
from pathlib import Path
from pydantic import BaseModel

from data_models import Agent, Interaction, Run

# Import settings
from config import settings

# Validate settings
settings.validate_required_settings()

# Request models for the new agent route
class PersonaRequest(BaseModel):
    name: str
    bio: str

class AgentRunRequest(BaseModel):
    url: str
    persona: PersonaRequest
    ux_question: str

class AgentRunResponse(BaseModel):
    agent_id: str
    run_id: str
    status: str
    message: str

class TranscriptSummaryRequest(BaseModel):
    agent_id: str
    
class TranscriptSummaryResponse(BaseModel):
    agent_id: str
    summary: str
    key_insights: List[str]
    user_sentiment: str
    success_rate: float
    recommendations: List[str]
    transcript: Optional[Dict[str, Any]] = None

class AskTheDataRequest(BaseModel):
    question: str
    agent_id: Optional[str] = None
    run_id: Optional[str] = None

class AskTheDataResponse(BaseModel):
    answer: str
    context_used: Dict[str, Any]

# Initialize FastAPI app
app = FastAPI(
    title="Agent API",
    description="API for managing agents, interactions, and runs",
    version="1.0.0"
)

# Add CORS middleware for lovable.dev and Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
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

# Initialize Supabase client
def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

# Agent runner and LLM functions
async def run_agent_background(agent_request: AgentRunRequest, run_id: str, agent_id: str):
    """Run the agent in the background"""
    try:
        # Import here to avoid circular imports
        import sys
        from pathlib import Path
        
        # Add the parent directory to path to import agent_worker
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        from agent_worker.agent import UXAgent
        from agent_worker.models.schemas import AgentInput, Persona, Viewport
        from agent_worker.services.agent_manager import AgentManager
        
        # Get API key from config
        api_key = settings.OPENAI_API_KEY
        
        # Create agent input with fixed defaults
        agent_input = AgentInput(
            run_id=run_id,
            url=agent_request.url,
            persona=Persona(
                name=agent_request.persona.name,
                bio=agent_request.persona.bio
            ),
            ux_question=agent_request.ux_question,
            viewport=Viewport.DESKTOP,  # Fixed
            step_budget=15,  # Fixed
            max_consecutive_errors=2,  # Fixed
            seed=19  # Fixed
        )
        
        # Initialize agent manager and run agent (will use venv by default)
        agent_manager = AgentManager()
        agent = UXAgent(api_key, agent_manager=agent_manager)
        
        # Set the agent_id since it was already created
        agent.agent_id = agent_id
        
        # Run the agent (it's already been created, just execute it)
        result = await agent.run(agent_input)
        
        print(f"Agent {result.agent_id} completed with {result.finish_reason}")
        
    except Exception as e:
        print(f"Error running agent: {e}")

async def generate_llm_summary(agent_id: str) -> Dict[str, Any]:
    """Generate LLM-powered summary of agent transcript"""
    try:
        import sys
        from pathlib import Path
        
        # Add the parent directory to path to import agent_worker
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        from agent_worker.services.agent_manager import AgentManager
        import openai
        import json
        
        # Get API key from config
        api_key = settings.OPENAI_API_KEY
        
        openai.api_key = api_key
        
        # Get agent data - specify the correct data directory
        venv_path = Path(sys.executable).parent.parent  # From venv/bin/python to venv/
        data_dir = venv_path / "agent_data"
        agent_manager = AgentManager(data_dir)
        agent_info = agent_manager.get_agent(agent_id)
        normalized_transcript = await agent_manager.get_normalized_transcript(agent_id)
        
        if not agent_info or not normalized_transcript:
            raise Exception(f"Agent {agent_id} or transcript not found")
        
        # Prepare transcript data for LLM
        transcript_summary = {
            "persona": normalized_transcript["persona"],
            "ux_question": agent_info["ux_question"],
            "url": agent_info["actual_url"],
            "total_steps": agent_info["total_steps"],
            "finish_reason": agent_info["finish_reason"],
            "overall_sentiment": agent_info["overall_sentiment"],
            "success_rate": agent_info["success_rate"],
            "session_duration": agent_info.get("session_duration_seconds", 0),
            "interactions": [
                {
                    "step": i["step"],
                    "intent": i["intent"],
                    "action": i["action_type"],
                    "result": i["result"],
                    "thought": i["thought"],
                    "sentiment": i["sentiment"]
                }
                for i in normalized_transcript["interactions"]
            ]
        }
        
        # Create LLM prompt
        prompt = f"""
Analyze this UX agent session objectively and provide realistic insights:

AGENT SESSION DATA:
{json.dumps(transcript_summary, indent=2)}

Please provide an honest, balanced analysis based ONLY on what actually happened:

1. SUMMARY: Factual 2-3 sentence overview of what occurred
2. KEY INSIGHTS: 3-5 objective findings based on actual user behavior  
3. USER SENTIMENT: Realistic assessment - only positive if truly positive, only negative if genuinely problematic
4. SUCCESS ANALYSIS: Honest evaluation of task completion and user experience
5. RECOMMENDATIONS: Practical suggestions based on observed issues or opportunities

IMPORTANT GUIDELINES:
- Be realistic - don't force positive sentiment if the user struggled
- Don't invent problems if the experience was genuinely smooth
- Focus on actual user behavior, not assumptions
- If the user failed or got frustrated, acknowledge it honestly
- If the user succeeded easily, don't create artificial pain points
- Base insights on evidence from the session data

Respond in JSON format:
{{
  "summary": "Factual overview of what happened...",
  "key_insights": ["evidence-based insight 1", "observed behavior 2", "actual finding 3"],
  "user_sentiment": "honest assessment based on actual user reactions",
  "success_analysis": "realistic evaluation of task completion and experience quality", 
  "recommendations": ["practical suggestion 1", "actionable improvement 2", "realistic enhancement 3"]
}}
"""
        
        # Call OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a UX analyst providing insights on user interaction data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Parse LLM response
        llm_response = response.choices[0].message.content
        
        # Try to parse as JSON, fallback to text
        try:
            analysis = json.loads(llm_response)
        except:
            analysis = {
                "summary": llm_response,
                "key_insights": ["Raw LLM response provided"],
                "user_sentiment": agent_info["overall_sentiment"],
                "success_analysis": f"Agent finished with {agent_info['finish_reason']}",
                "recommendations": ["Review raw LLM response for insights"]
            }
        
        return analysis
        
    except Exception as e:
        return {
            "summary": f"Error generating summary: {str(e)}",
            "key_insights": ["Analysis failed"],
            "user_sentiment": "unknown",
            "success_analysis": "Could not analyze",
            "recommendations": ["Check system configuration"]
        }


@app.options("/")
async def options_root():
    """Handle OPTIONS request for root endpoint"""
    return {"message": "OK"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Agent API is running", "version": "1.0.0"}


@app.options("/health")
async def options_health():
    """Handle OPTIONS request for health endpoint"""
    return {"message": "OK"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "agent-api"}


@app.options("/agent/run")
async def options_run_agent():
    """Handle OPTIONS request for agent run endpoint"""
    return {"message": "OK"}

@app.post("/agent/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest, background_tasks: BackgroundTasks):
    """
    Create and run an agent with the provided persona and UX question.
    Fixed parameters: viewport=DESKTOP, step_budget=15, max_consecutive_errors=2, seed=19
    """
    try:
        # Import here to avoid circular imports
        import sys
        from pathlib import Path
        
        # Add the parent directory to path to import agent_worker
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        from agent_worker.agent import UXAgent
        from agent_worker.models.schemas import AgentInput, Persona, Viewport
        from agent_worker.services.agent_manager import AgentManager
        
        # Generate unique run_id
        run_id = f"api_run_{uuid4()}"
        
        # Get API key from config
        api_key = settings.OPENAI_API_KEY
        
        # Create agent input with fixed defaults
        agent_input = AgentInput(
            run_id=run_id,
            url=request.url,
            persona=Persona(
                name=request.persona.name,
                bio=request.persona.bio
            ),
            ux_question=request.ux_question,
            viewport=Viewport.DESKTOP,  # Fixed
            step_budget=15,  # Fixed
            max_consecutive_errors=2,  # Fixed
            seed=19  # Fixed
        )
        
        # Initialize agent manager and create agent to get the ID
        agent_manager = AgentManager()
        
        # Create the agent first to get the ID
        agent_id = agent_manager.create_agent(
            run_id=run_id,
            persona_name=request.persona.name,
            persona_bio=request.persona.bio,
            url=request.url,
            ux_question=request.ux_question
        )
        
        # Start agent execution in background
        background_tasks.add_task(run_agent_background, request, run_id, agent_id)
        
        return AgentRunResponse(
            agent_id=agent_id,  # Now we have the actual agent ID
            run_id=run_id,
            status="started",
            message=f"Agent started for {request.persona.name} on {request.url}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start agent: {str(e)}")


@app.options("/agent/summary")
async def options_agent_summary():
    """Handle OPTIONS request for agent summary endpoint"""
    return {"message": "OK"}

@app.post("/agent/summary", response_model=TranscriptSummaryResponse)
async def get_agent_summary(request: TranscriptSummaryRequest):
    """
    Generate LLM-powered summary and insights from agent transcript
    """
    try:
        # Generate LLM analysis
        analysis = await generate_llm_summary(request.agent_id)
        
        # Get agent info for additional context
        import sys
        from pathlib import Path
        
        # Add the parent directory to path to import agent_worker
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        from agent_worker.services.agent_manager import AgentManager
        
        # Specify the correct data directory
        venv_path = Path(sys.executable).parent.parent  # From venv/bin/python to venv/
        data_dir = venv_path / "agent_data"
        agent_manager = AgentManager(data_dir)
        agent_info = agent_manager.get_agent(request.agent_id)
        
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent {request.agent_id} not found")
        
        # Get the normalized transcript for the frontend
        normalized_transcript = await agent_manager.get_normalized_transcript(request.agent_id)
        
        return TranscriptSummaryResponse(
            agent_id=request.agent_id,
            summary=analysis.get("summary", "No summary available"),
            key_insights=analysis.get("key_insights", []),
            user_sentiment=analysis.get("user_sentiment", agent_info.get("overall_sentiment", "unknown")),
            success_rate=agent_info.get("success_rate", 0.0),
            recommendations=analysis.get("recommendations", []),
            transcript=normalized_transcript
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@app.options("/agent/{agent_id}/status")
async def options_agent_status(agent_id: str):
    """Handle OPTIONS request for agent status endpoint"""
    return {"message": "OK"}

@app.get("/agent/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get current status of an agent"""
    try:
        import sys
        from pathlib import Path
        
        # Add the parent directory to path to import agent_worker
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        from agent_worker.services.agent_manager import AgentManager
        
        agent_manager = AgentManager()
        agent_info = agent_manager.get_agent(agent_id)
        
        if not agent_info:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return {
            "agent_id": agent_id,
            "status": agent_info["status"],
            "persona_name": agent_info["persona_name"],
            "url": agent_info.get("actual_url", agent_info["url"]),
            "finish_reason": agent_info.get("finish_reason"),
            "overall_sentiment": agent_info.get("overall_sentiment"),
            "success_rate": agent_info.get("success_rate"),
            "total_steps": agent_info.get("total_steps"),
            "created_at": agent_info["created_at"],
            "updated_at": agent_info["updated_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


@app.options("/agents")
async def options_agents():
    """Handle OPTIONS request for agents endpoint"""
    return {"message": "OK"}

@app.get("/agents")
async def list_agents(run_id: Optional[str] = None, status: Optional[str] = None):
    """List all agents with optional filtering"""
    try:
        import sys
        from pathlib import Path
        
        # Add the parent directory to path to import agent_worker
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        from agent_worker.services.agent_manager import AgentManager
        
        agent_manager = AgentManager()
        
        if run_id:
            agents = agent_manager.list_agents_by_run(run_id)
        elif status:
            agents = agent_manager.list_agents_by_status(status)
        else:
            agents = agent_manager.list_all_agents()
        
        return {
            "total": len(agents),
            "agents": agents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@app.options("/runs")
async def options_runs():
    """Handle OPTIONS request for runs endpoint"""
    return {"message": "OK"}

@app.post("/runs")
async def create_run(run: Run, supabase: Client = Depends(get_supabase)):
    """Create a new run and return the run_id"""
    try:
        # Convert Pydantic model to dict
        run_data = run.model_dump()
        
        # Insert into Supabase
        response = supabase.table("run").insert(run_data).execute()
            #TODO: Kick off the agent and begin the run process of going to the website and interacting with the website, make sure we pass in the run_id as well 
            
            
        if response.data and len(response.data) > 0:
            return {"run_id": response.data[0]["run_id"]}
        else:
            raise HTTPException(status_code=400, detail="Failed to create run")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.options("/runs/{run_id}/agents")
async def options_run_agents(run_id: UUID):
    """Handle OPTIONS request for run agents endpoint"""
    return {"message": "OK"}

@app.get("/runs/{run_id}/agents", response_model=List[Agent])
async def get_agents_for_run(run_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get list of agents for the specified run"""
    try:
        response = supabase.table("agent").select("*").eq("run_id", str(run_id)).execute()
        return [Agent(**agent) for agent in response.data] if response.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.options("/agents/{agent_id}/interactions")
async def options_agent_interactions(agent_id: UUID):
    """Handle OPTIONS request for agent interactions endpoint"""
    return {"message": "OK"}

@app.get("/agents/{agent_id}/interactions", response_model=List[Interaction])
async def get_interactions_for_agent(agent_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get steps (interactions) for the specified agent"""
    try:
        response = supabase.table("interaction").select("*").eq("agent_id", str(agent_id)).execute()
        return [Interaction(**interaction) for interaction in response.data] if response.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.options("/ask-the-data")
async def options_ask_the_data():
    """Handle OPTIONS request for ask-the-data endpoint"""
    return {"message": "OK"}

@app.post("/ask-the-data", response_model=AskTheDataResponse)
async def ask_the_data(request: AskTheDataRequest):
    """
    Process user questions about the testing data using OpenAI.
    Bundles relevant context and sends to OpenAI for analysis.
    """
    try:
        import openai
        import json
        import sys
        from pathlib import Path
        
        # Add the parent directory to path to import agent_worker
        parent_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(parent_dir))
        
        from agent_worker.services.agent_manager import AgentManager
        
        # Get API key from config
        api_key = settings.OPENAI_API_KEY
        
        openai.api_key = api_key
        agent_manager = AgentManager()
        
        # Gather context based on what's provided
        context = {
            "question": request.question,
            "agents": [],
            "runs": []
        }
        
        # If agent_id is provided, get specific agent data
        if request.agent_id:
            agent_info = agent_manager.get_agent(request.agent_id)
            if agent_info:
                # Get normalized transcript for detailed data
                normalized_transcript = await agent_manager.get_normalized_transcript(request.agent_id)
                
                context["agents"].append({
                    "agent_id": request.agent_id,
                    "persona": agent_info["persona_name"],
                    "url": agent_info.get("actual_url", agent_info["url"]),
                    "ux_question": agent_info["ux_question"],
                    "status": agent_info["status"],
                    "finish_reason": agent_info.get("finish_reason"),
                    "overall_sentiment": agent_info.get("overall_sentiment"),
                    "success_rate": agent_info.get("success_rate"),
                    "total_steps": agent_info.get("total_steps"),
                    "session_duration": agent_info.get("session_duration_seconds", 0),
                    "transcript": normalized_transcript if normalized_transcript else None
                })
        
        # If run_id is provided, get all agents for that run
        elif request.run_id:
            agents = agent_manager.list_agents_by_run(request.run_id)
            for agent in agents:
                context["agents"].append({
                    "agent_id": agent["agent_id"],
                    "persona": agent["persona_name"],
                    "url": agent.get("actual_url", agent["url"]),
                    "ux_question": agent["ux_question"],
                    "status": agent["status"],
                    "finish_reason": agent.get("finish_reason"),
                    "overall_sentiment": agent.get("overall_sentiment"),
                    "success_rate": agent.get("success_rate"),
                    "total_steps": agent.get("total_steps")
                })
            context["run_summary"] = {
                "run_id": request.run_id,
                "total_agents": len(agents),
                "average_success_rate": sum(a.get("success_rate", 0) for a in agents) / len(agents) if agents else 0
            }
        
        # If neither is provided, get recent agent data
        else:
            recent_agents = agent_manager.list_all_agents()[:10]  # Get last 10 agents
            for agent in recent_agents:
                context["agents"].append({
                    "agent_id": agent["agent_id"],
                    "persona": agent["persona_name"],
                    "url": agent.get("actual_url", agent["url"]),
                    "ux_question": agent["ux_question"],
                    "status": agent["status"],
                    "finish_reason": agent.get("finish_reason"),
                    "overall_sentiment": agent.get("overall_sentiment"),
                    "success_rate": agent.get("success_rate")
                })
        
        # Create prompt for OpenAI
        system_prompt = """You are a UX testing data analyst assistant. Answer questions about UX testing sessions based on the provided context.
Be concise, accurate, and focus on insights that would be valuable for improving user experience.
If the data doesn't contain enough information to answer the question fully, acknowledge what you can answer and what's missing."""
        
        user_prompt = f"""Based on the following UX testing data, please answer this question: {request.question}

CONTEXT DATA:
{json.dumps(context, indent=2)}

Please provide a clear, helpful answer based on the available data."""
        
        # Call OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        answer = response.choices[0].message.content
        
        return AskTheDataResponse(
            answer=answer,
            context_used={
                "agent_count": len(context["agents"]),
                "agent_ids": [a["agent_id"] for a in context["agents"]],
                "run_id": request.run_id if request.run_id else None,
                "data_scope": "specific_agent" if request.agent_id else ("run" if request.run_id else "recent_agents")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process question: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)