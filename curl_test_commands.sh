#!/bin/bash
# =============================================================================
# CURL TEST COMMANDS FOR AGENT API
# =============================================================================
# 
# Usage: 
#   1. Make sure your backend is running: python backend/main.py
#   2. Run any of these commands in terminal
#   3. Replace URLs and personas as needed
#
# =============================================================================

API_BASE="http://localhost:8000"

echo "🧪 AGENT API CURL TEST COMMANDS"
echo "==============================="
echo ""

# Check if API is running
echo "1️⃣  HEALTH CHECK:"
echo "curl -X GET $API_BASE/health | jq"
echo ""

# Test 1: Create agent for a website
echo "2️⃣  CREATE AGENT (Test Website):"
cat << 'EOF'
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "persona": {
      "name": "Jordan Kim",
      "bio": "Jordan is a 28-year-old small business owner looking for web hosting solutions. Jordan values clear pricing, reliable support, and easy setup processes."
    },
    "ux_question": "I want to understand what services this company offers and find their pricing information. Navigate the website to explore their main offerings and see how transparent their pricing is."
  }' | jq
EOF
echo ""

# Test 2: Create agent for e-commerce site
echo "3️⃣  CREATE AGENT (E-commerce Test):"
cat << 'EOF'
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.amazon.com",
    "persona": {
      "name": "Maria Santos",
      "bio": "Maria is a 35-year-old working mother who needs to quickly find and purchase a laptop for her teenager. She values efficiency, clear product information, and competitive pricing."
    },
    "ux_question": "I need to find a good laptop for my teenager under $800. Search for laptops, filter by price, and find a suitable option with good reviews and specifications."
  }' | jq
EOF
echo ""

# Test 3: Create agent for SaaS website
echo "4️⃣  CREATE AGENT (SaaS Website Test):"
cat << 'EOF'
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.notion.so",
    "persona": {
      "name": "Alex Chen",
      "bio": "Alex is a 31-year-old startup founder who needs a productivity tool for their remote team. Alex wants to understand pricing, features, and how easy it is to get started."
    },
    "ux_question": "I want to explore Notion for my startup team. Find information about team features, pricing plans, and see how easy it is to sign up or start a trial."
  }' | jq
EOF
echo ""

# Test 4: Create agent for buggy/problematic website
echo "5️⃣  CREATE AGENT (Problematic Website Test):"
cat << 'EOF'
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://buggy.justtestit.org",
    "persona": {
      "name": "Sam Taylor",
      "bio": "Sam is a 42-year-old consultant who gets frustrated with poorly designed websites. Sam has limited patience for broken features and values efficiency above all."
    },
    "ux_question": "I need to find contact information and understand what services this company provides. Navigate the site efficiently and locate their contact details and service offerings."
  }' | jq
EOF
echo ""

# Test 5: List all agents
echo "6️⃣  LIST ALL AGENTS:"
echo "curl -X GET $API_BASE/agents | jq"
echo ""

# Test 6: Get specific agent status (replace AGENT_ID)
echo "7️⃣  GET AGENT STATUS:"
echo "curl -X GET $API_BASE/agent/AGENT_ID/status | jq"
echo ""

# Test 7: Get LLM insights for agent (replace AGENT_ID)
echo "8️⃣  GET LLM INSIGHTS:"
cat << 'EOF'
curl -X POST http://localhost:8000/agent/summary \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "AGENT_ID"
  }' | jq
EOF
echo ""

echo "🔄 COMPLETE WORKFLOW EXAMPLE:"
echo "============================="
echo ""
echo "Step 1: Create an agent and note the run_id from response"
echo "Step 2: Wait a few seconds for completion"
echo "Step 3: List agents to find your agent_id"
echo "Step 4: Get LLM insights using the agent_id"
echo ""

# Complete workflow example
echo "📋 COPY-PASTE READY COMMANDS:"
echo "=============================="
echo ""

echo "# 1. Test with your own website (replace URL):"
echo 'curl -X POST http://localhost:8000/agent/run \'
echo '  -H "Content-Type: application/json" \'
echo '  -d "{"'
echo '    \"url\": \"YOUR_WEBSITE_HERE\",'
echo '    \"persona\": {'
echo '      \"name\": \"Test User\",'
echo '      \"bio\": \"A user testing this website for usability and functionality.\"'
echo '    },'
echo '    \"ux_question\": \"Explore this website and evaluate how easy it is to find key information and complete important tasks.\"'
echo '  }" | jq'
echo ""

echo "# 2. Check if agent completed:"
echo "curl -X GET http://localhost:8000/agents | jq '.agents[-1]'"
echo ""

echo "# 3. Get LLM insights (replace AGENT_ID with actual ID):"
echo 'curl -X POST http://localhost:8000/agent/summary \'
echo '  -H "Content-Type: application/json" \'
echo '  -d "{\"agent_id\": \"AGENT_ID\"}" | jq'
echo ""

echo "💡 QUICK TEST WEBSITES:"
echo "======================="
echo "✅ Good UX: https://www.stripe.com, https://www.apple.com"
echo "⚠️  Average UX: https://example.com, https://www.wikipedia.org"
echo "❌ Buggy UX: https://buggy.justtestit.org"
echo ""

echo "🎯 WHAT TO EXPECT:"
echo "=================="
echo "- Agent creation returns: run_id, status"
echo "- Agent completion takes: 5-30 seconds depending on complexity"
echo "- LLM insights include: summary, key_insights, user_sentiment, success_analysis, recommendations"
echo "- All data stored in: /Users/ahmed/ArchetypeV2/venv/agent_data/"
echo ""
