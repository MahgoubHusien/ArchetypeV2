# 🚀 HOW TO RUN THE AGENT API APPLICATION

## 📋 Prerequisites

- Python 3.8+
- Virtual environment activated
- OpenAI API key

## 🏁 Step-by-Step Startup Guide

### 1. Navigate to Project Directory

```bash
cd /Users/ahmed/ArchetypeV2
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Set Environment Variables

```bash
export OPENAI_API_KEY='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'
export PYTHONPATH=/Users/ahmed/ArchetypeV2:$PYTHONPATH
```

### 4. Start the Backend Server

```bash
python backend/main.py
```

You should see:

```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 5. Test API Health (New Terminal)

```bash
curl -X GET http://localhost:8000/health | jq
```

Expected response:

```json
{
  "status": "healthy",
  "service": "agent-api"
}
```

---

## 🧪 CURL TESTING COMMANDS

### ✅ Quick Test with Any Website

**Step 1: Create Agent**

```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://stripe.com",
    "persona": {
      "name": "Sarah Johnson",
      "bio": "Sarah is a startup founder evaluating payment solutions for her e-commerce business."
    },
    "ux_question": "I want to understand Stripe pricing and see how easy it is to get started with their payment platform."
  }' | jq
```

**Expected Response:**

```json
{
  "run_id": "api_run_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "started",
  "message": "Agent started for Sarah Johnson on https://stripe.com"
}
```

**Step 2: Wait for Completion (5-15 seconds)**

```bash
curl -X GET http://localhost:8000/agents | jq '.agents[-1]'
```

Wait until `status` shows `"completed"`, `"failed"`, or `"dropped_off"`

**Step 3: Get LLM Insights** (Replace AGENT_ID with actual ID from step 2)

```bash
curl -X POST http://localhost:8000/agent/summary \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "AGENT_ID"}' | jq
```

---

## 🎯 TESTING DIFFERENT SCENARIOS

### 1. Good Website Experience

```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.apple.com",
    "persona": {
      "name": "Mike Chen",
      "bio": "Tech enthusiast looking for the latest iPhone information and pricing."
    },
    "ux_question": "Find information about the latest iPhone models, compare features, and locate pricing details."
  }' | jq
```

### 2. E-commerce Test

```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.amazon.com",
    "persona": {
      "name": "Lisa Martinez",
      "bio": "Busy parent shopping for educational toys for a 7-year-old child."
    },
    "ux_question": "Search for educational toys suitable for a 7-year-old, filter results, and find highly-rated options under $50."
  }' | jq
```

### 3. Buggy Website Test (Realistic Negative Feedback)

```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://buggy.justtestit.org",
    "persona": {
      "name": "Alex Thompson",
      "bio": "Frustrated user with limited patience for broken websites and technical issues."
    },
    "ux_question": "Find contact information and company details quickly. I need this information urgently."
  }' | jq
```

---

## 📊 MONITORING AND DEBUGGING

### Check All Agents

```bash
curl -X GET http://localhost:8000/agents | jq
```

### Get Specific Agent Status

```bash
curl -X GET http://localhost:8000/agent/AGENT_ID/status | jq
```

### Filter Agents by Status

```bash
# Completed agents
curl -X GET "http://localhost:8000/agents?status=completed" | jq

# Failed agents
curl -X GET "http://localhost:8000/agents?status=failed" | jq
```

---

## 🔧 TROUBLESHOOTING

### Backend Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
pkill -f "python.*main.py"

# Restart
python backend/main.py
```

### Import Errors

```bash
# Make sure you're in the right directory
pwd
# Should show: /Users/ahmed/ArchetypeV2

# Check virtual environment
which python
# Should show: /Users/ahmed/ArchetypeV2/venv/bin/python

# Reinstall dependencies if needed
pip install -r requirements.txt
```

### API Not Responding

```bash
# Check health endpoint
curl -X GET http://localhost:8000/health

# Check if server is running
ps aux | grep "python.*main.py"
```

---

## 💾 DATA STORAGE

All agent data is stored in:

```
/Users/ahmed/ArchetypeV2/venv/agent_data/
├── agent_registry.json       # All agent metadata
├── transcripts/              # Processed transcripts
│   └── agent_xxxxx_normalized.json
└── [run_folders]/           # Raw data + screenshots
    ├── agent_xxxxx_transcript.json
    └── agent_xxxxx_step*.png
```

---

## 🎉 COMPLETE WORKFLOW EXAMPLE

```bash
# 1. Start the application
cd /Users/ahmed/ArchetypeV2
source venv/bin/activate
export OPENAI_API_KEY='your-key-here'
export PYTHONPATH=/Users/ahmed/ArchetypeV2:$PYTHONPATH
python backend/main.py &

# 2. Test with your website
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "YOUR_WEBSITE_HERE",
    "persona": {
      "name": "Test User",
      "bio": "A potential customer evaluating this website."
    },
    "ux_question": "Explore the website and evaluate how easy it is to find key information and complete important tasks."
  }' | jq

# 3. Wait for completion
sleep 10

# 4. Get the agent ID
AGENT_ID=$(curl -s http://localhost:8000/agents | jq -r '.agents[-1].agent_id')
echo "Agent ID: $AGENT_ID"

# 5. Get LLM insights
curl -X POST http://localhost:8000/agent/summary \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\": \"$AGENT_ID\"}" | jq
```

---

## 🔑 API ENDPOINTS SUMMARY

| Method | Endpoint             | Description          |
| ------ | -------------------- | -------------------- |
| `GET`  | `/health`            | Check API health     |
| `POST` | `/agent/run`         | Create and run agent |
| `GET`  | `/agents`            | List all agents      |
| `GET`  | `/agent/{id}/status` | Get agent status     |
| `POST` | `/agent/summary`     | Get LLM insights     |

---

## ⚡ ONE-LINER STARTUP

```bash
cd /Users/ahmed/ArchetypeV2 && source venv/bin/activate && export OPENAI_API_KEY='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' && export PYTHONPATH=/Users/ahmed/ArchetypeV2:$PYTHONPATH && python backend/main.py
```
