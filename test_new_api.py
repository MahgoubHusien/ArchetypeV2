#!/usr/bin/env python3
"""
Test the new agent API routes
"""

import requests
import json
import time
from typing import Dict, Any

API_BASE = "http://localhost:8000"

def test_agent_api():
    """Test the complete agent workflow via API"""
    
    print("🚀 Testing New Agent API Routes")
    print("=" * 40)
    
    # 1. Test the exact frontend request format
    print("\n📡 1. Creating Agent (Frontend Request Format)")
    print("-" * 45)
    
    # This matches your demo_input structure
    agent_request = {
        "url": "https://buggy.justtestit.org/",
        "persona": {
            "name": "Sam",
            "bio": "26-year-old kid runs into a website and wants to know what it is"
        },
        "ux_question": "What is this website about?"
    }
    
    print(f"📝 Request: {json.dumps(agent_request, indent=2)}")
    
    try:
        response = requests.post(f"{API_BASE}/agent/run", json=agent_request)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Agent Started!")
            print(f"   Run ID: {result['run_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            
            run_id = result['run_id']
            
            # 2. Poll for agent completion
            print(f"\n⏳ 2. Polling for Agent Completion")
            print("-" * 35)
            
            # Wait for agents to be created and get agent_id
            print("Waiting for agent to be created...")
            time.sleep(3)
            
            # List agents for this run
            agents_response = requests.get(f"{API_BASE}/agents?run_id={run_id}")
            if agents_response.status_code == 200:
                agents_data = agents_response.json()
                
                if agents_data["total"] > 0:
                    agent_id = agents_data["agents"][0]["agent_id"]
                    print(f"✅ Found Agent: {agent_id}")
                    
                    # Wait for completion
                    max_polls = 10
                    for i in range(max_polls):
                        status_response = requests.get(f"{API_BASE}/agent/{agent_id}/status")
                        
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            print(f"   Poll {i+1}: Status = {status_data['status']}")
                            
                            if status_data['status'] in ['completed', 'failed', 'dropped_off']:
                                print(f"✅ Agent Completed!")
                                print(f"   Final Status: {status_data['status']}")
                                print(f"   Finish Reason: {status_data.get('finish_reason', 'N/A')}")
                                print(f"   Sentiment: {status_data.get('overall_sentiment', 'N/A')}")
                                print(f"   Success Rate: {status_data.get('success_rate', 0)*100:.1f}%")
                                print(f"   Total Steps: {status_data.get('total_steps', 0)}")
                                break
                        
                        time.sleep(5)  # Wait 5 seconds between polls
                    
                    # 3. Generate LLM Summary
                    print(f"\n🧠 3. Generating LLM Summary")
                    print("-" * 28)
                    
                    summary_request = {"agent_id": agent_id}
                    summary_response = requests.post(f"{API_BASE}/agent/summary", json=summary_request)
                    
                    if summary_response.status_code == 200:
                        summary_data = summary_response.json()
                        
                        print(f"✅ LLM Analysis Complete!")
                        print(f"\n📋 SUMMARY:")
                        print(f"   {summary_data['summary']}")
                        
                        print(f"\n🔍 KEY INSIGHTS:")
                        for insight in summary_data['key_insights']:
                            print(f"   • {insight}")
                        
                        print(f"\n😊 USER SENTIMENT:")
                        print(f"   {summary_data['user_sentiment']}")
                        
                        print(f"\n🎯 SUCCESS RATE:")
                        print(f"   {summary_data['success_rate']*100:.1f}%")
                        
                        print(f"\n💡 RECOMMENDATIONS:")
                        for rec in summary_data['recommendations']:
                            print(f"   • {rec}")
                        
                    else:
                        print(f"❌ Summary failed: {summary_response.status_code}")
                        print(f"   Error: {summary_response.text}")
                
                else:
                    print("❌ No agents found for this run yet")
            
        else:
            print(f"❌ Agent creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("   Make sure the backend is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_arcade_agent():
    """Test with Arcade.ai like we did before"""
    
    print("\n\n🎨 Testing Arcade.ai Agent via API")
    print("=" * 35)
    
    arcade_request = {
        "url": "https://www.arcade.ai/sell",
        "persona": {
            "name": "Maya",
            "bio": "Maya is a 31-year-old interior designer who wants to explore AI-powered product creation tools."
        },
        "ux_question": "I want to explore the Create with AI button/feature on Arcade.ai. Navigate to and click on Create with AI, explore the interface."
    }
    
    try:
        response = requests.post(f"{API_BASE}/agent/run", json=arcade_request)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Arcade Agent Started!")
            print(f"   Run ID: {result['run_id']}")
            print(f"   Message: {result['message']}")
            
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_api_usage():
    """Show example API usage"""
    
    print("\n\n📚 API Usage Examples")
    print("=" * 22)
    
    print("""
🔥 NEW API ENDPOINTS:

1. POST /agent/run
   - Frontend sends: persona + ux_question + url
   - Fixed params: viewport=DESKTOP, step_budget=15, max_consecutive_errors=2, seed=19
   - Returns: run_id and status
   
2. GET /agent/{agent_id}/status
   - Check agent progress and results
   
3. POST /agent/summary  
   - Get LLM-powered insights from transcript
   - JSON with summary, insights, sentiment, recommendations
   
4. GET /agents?run_id=xxx
   - List agents for a run

📝 EXAMPLE FRONTEND REQUEST:
```javascript
const response = await fetch('/agent/run', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: "https://buggy.justtestit.org/",
    persona: {
      name: "Sam", 
      bio: "26-year-old kid runs into a website and wants to know what it is"
    },
    ux_question: "What is this website about?"
  })
});
```

🤖 WORKFLOW:
1. Frontend sends persona + question → /agent/run
2. Backend creates agent with fixed params, starts in background  
3. Frontend polls /agent/{id}/status until complete
4. Frontend calls /agent/summary for LLM insights
""")

if __name__ == "__main__":
    # Run tests
    test_agent_api()
    test_arcade_agent()
    show_api_usage()
    
    print("\n✨ API Testing Complete!")
    print("\nTo start the backend server:")
    print("cd backend && python main.py")
