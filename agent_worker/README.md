# Agent Worker for UX Testing

This agent simulates personas interacting with websites to gather UX insights.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Create `.env` file:
```bash
cp .env.example .env
# Add your OPENAI_API_KEY
```

## Usage

Run the demo:
```bash
python demo.py
```

## Architecture

- `agent.py` - Main agent loop (plan → act → screenshot → log)
- `models/schemas.py` - Data models matching backend schemas
- `services/page_digest.py` - Extract page information for planning
- `services/planner.py` - LLM-based action planning
- `services/action_executor.py` - Execute browser actions
- `utils/storage.py` - Save/load JSON transcripts
- `data/` - Stores screenshots and transcripts per run_id
- `static/` - Serves screenshots via web URLs

## Output Format

Agent outputs match the backend schema:
```json
{
  "agent_id": "agent_abc123",
  "persona": {"name": "Amy", "bio": "..."},
  "session": {"url": "...", "device": "mobile", "browser": "chromium"},
  "interactions": [
    {
      "step": 1,
      "intent": "Click Edit with AI button",
      "action_type": "click",
      "selector": "text=Edit with AI",
      "result": "clicked",
      "thought": "Testing unclear CTA",
      "ts": "2025-08-22T17:11:02Z",
      "screenshot": "/static/run_001/agent_abc_step1.png"
    }
  ],
  "finish_reason": "step_budget_reached"
}
```