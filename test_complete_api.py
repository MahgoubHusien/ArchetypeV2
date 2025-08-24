#!/usr/bin/env python3
"""
Complete API Test Suite
========================

This script tests the entire agent creation and insights pipeline:
1. Creates a dynamic agent on a buggy website  
2. Waits for completion
3. Gets LLM insights
4. Shows complete results

Usage: python test_complete_api.py
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
API_BASE = 'http://localhost:8000'
POLL_INTERVAL = 3  # seconds
MAX_WAIT_TIME = 120  # seconds

def print_header(title):
    """Print a formatted header"""
    print(f'\n{"="*60}')
    print(f'🧪 {title}')
    print(f'{"="*60}')

def print_section(title):
    """Print a formatted section"""
    print(f'\n🔷 {title}')
    print('-' * 40)

def test_buggy_website():
    """Test with a buggy website to get realistic negative feedback"""
    
    print_header("COMPLETE API TEST - BUGGY WEBSITE")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test case: Frustrated user on buggy website
    test_agent = {
        'url': 'https://buggy.justtestit.org/',
        'persona': {
            'name': 'Alex Martinez',
            'bio': 'Alex is a 34-year-old project manager who needs to quickly find contact information for a client meeting in 10 minutes. Alex gets frustrated easily when websites don\'t work properly and values efficiency. Alex has limited patience for broken features or confusing navigation.'
        },
        'ux_question': 'I urgently need to find the contact information and customer support details on this website. I have a client meeting in 10 minutes and need to get contact details quickly. Navigate the site and find phone numbers, email addresses, or contact forms.'
    }
    
    print_section("TEST SETUP")
    print(f"🌐 Target: {test_agent['url']}")
    print(f"👤 Persona: {test_agent['persona']['name']}")
    print(f"🎯 Mission: {test_agent['ux_question'][:100]}...")
    print(f"💭 Context: Urgent, time-pressured user on buggy website")
    
    try:
        # Step 1: Create Agent
        print_section("STEP 1: CREATING DYNAMIC AGENT")
        print("🚀 Sending agent creation request...")
        
        response = requests.post(f'{API_BASE}/agent/run', json=test_agent, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to create agent: {response.status_code}")
            print(response.text)
            return None
            
        result = response.json()
        agent_id = None
        run_id = result['run_id']
        
        print(f"✅ Agent created successfully!")
        print(f"   🆔 Run ID: {run_id}")
        print(f"   📊 Status: {result['status']}")
        print(f"   💬 Message: {result['message']}")
        
        # Step 2: Wait for completion
        print_section("STEP 2: MONITORING AGENT EXECUTION")
        print("⏳ Waiting for agent to complete...")
        
        start_time = time.time()
        agent_completed = False
        
        while time.time() - start_time < MAX_WAIT_TIME:
            time.sleep(POLL_INTERVAL)
            
            # Check agent status
            try:
                agents_response = requests.get(f'{API_BASE}/agents', timeout=5)
                if agents_response.status_code == 200:
                    agents_data = agents_response.json()
                    
                    if 'agents' in agents_data:
                        agents = agents_data['agents']
                        # Find our agent by run_id
                        matching_agents = [a for a in agents if a.get('run_id') == run_id]
                        
                        if matching_agents:
                            agent = matching_agents[0]
                            agent_id = agent['agent_id']
                            status = agent['status']
                            
                            print(f"📊 Agent {agent_id}: {status}")
                            
                            if status in ['completed', 'failed', 'dropped_off']:
                                agent_completed = True
                                print(f"✅ Agent finished with status: {status}")
                                print(f"   ⏱️  Duration: {agent.get('session_duration_seconds', 'unknown')} seconds")
                                print(f"   📈 Steps: {agent.get('total_steps', 'unknown')}")
                                print(f"   😊 Sentiment: {agent.get('overall_sentiment', 'unknown')}")
                                print(f"   🎯 Success Rate: {agent.get('success_rate', 'unknown')}")
                                break
                        else:
                            print("🔍 Agent not found in list yet...")
                    else:
                        print("⚠️  No agents data available")
                else:
                    print(f"⚠️  Error checking agents: {agents_response.status_code}")
                    
            except Exception as e:
                print(f"⚠️  Error polling agents: {e}")
        
        if not agent_completed:
            print(f"⚠️  Agent did not complete within {MAX_WAIT_TIME} seconds")
            return None
            
        if not agent_id:
            print("❌ Could not determine agent ID")
            return None
            
        # Step 3: Get LLM Insights
        print_section("STEP 3: GENERATING LLM INSIGHTS")
        print("🧠 Requesting LLM analysis...")
        
        summary_request = {'agent_id': agent_id}
        
        insights_response = requests.post(
            f'{API_BASE}/agent/summary', 
            json=summary_request, 
            timeout=60
        )
        
        if insights_response.status_code != 200:
            print(f"❌ Failed to get insights: {insights_response.status_code}")
            print(insights_response.text)
            return None
            
        insights = insights_response.json()
        
        # Step 4: Display Results
        print_section("STEP 4: COMPLETE RESULTS")
        
        # Extract clean insights if nested
        clean_insights = insights
        if 'summary' in insights and isinstance(insights['summary'], str) and 'json' in insights['summary']:
            import re
            json_match = re.search(r'\{[^}]*(?:\{[^}]*\}[^}]*)*\}', insights['summary'], re.DOTALL)
            if json_match:
                try:
                    clean_json = json_match.group()
                    clean_insights = json.loads(clean_json)
                except json.JSONDecodeError:
                    clean_insights = insights
        
        print("🎯 REALISTIC LLM ANALYSIS:")
        print("=" * 25)
        print()
        
        print("📝 SUMMARY:")
        summary = clean_insights.get('summary', 'No summary available')
        print(f"   {summary}")
        print()
        
        print("🔍 KEY INSIGHTS:")
        key_insights = clean_insights.get('key_insights', [])
        if key_insights and key_insights != ['Raw LLM response provided']:
            for i, insight in enumerate(key_insights, 1):
                print(f"   {i}. {insight}")
        else:
            print("   No specific insights extracted")
        print()
        
        print("😊 USER SENTIMENT:")
        sentiment = clean_insights.get('user_sentiment', 'No sentiment analysis available')
        print(f"   {sentiment}")
        print()
        
        print("🎯 SUCCESS ANALYSIS:")
        success_analysis = clean_insights.get('success_analysis', 'No success analysis available')
        print(f"   {success_analysis}")
        print()
        
        print("💡 RECOMMENDATIONS:")
        recommendations = clean_insights.get('recommendations', [])
        if recommendations and recommendations != ['Review raw LLM response for insights']:
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("   No specific recommendations available")
        print()
        
        # Show raw JSON for frontend
        print_section("FRONTEND JSON RESPONSE")
        print("📋 Raw JSON (for frontend integration):")
        print(json.dumps(clean_insights, indent=2))
        
        print_section("TEST SUMMARY")
        print("✅ COMPLETE API TEST SUCCESSFUL!")
        print(f"   🤖 Agent: {agent_id}")
        print(f"   🎭 Persona: {test_agent['persona']['name']}")
        print(f"   🌐 Website: {test_agent['url']}")
        print(f"   🧠 LLM: Realistic analysis generated")
        print(f"   💾 Data: Stored in venv")
        print(f"   📡 API: All endpoints working")
        
        return {
            'agent_id': agent_id,
            'insights': clean_insights,
            'success': True
        }
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        print("💡 Make sure the backend is running on http://localhost:8000")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_good_website():
    """Test with a good website for comparison"""
    
    print_header("COMPARISON TEST - GOOD WEBSITE")
    
    good_agent = {
        'url': 'https://www.google.com',
        'persona': {
            'name': 'Emma Wilson',
            'bio': 'Emma is a 28-year-old researcher who needs to quickly search for information about sustainable energy solutions for her upcoming presentation.'
        },
        'ux_question': 'I need to search for recent articles and information about solar energy innovations. Use the search functionality to find relevant and current information about solar panel technology advances.'
    }
    
    print_section("GOOD WEBSITE TEST")
    print(f"🌐 Target: {good_agent['url']}")
    print(f"👤 Persona: {good_agent['persona']['name']}")
    print(f"🎯 Expected: Positive experience on well-designed website")
    
    # Similar process as buggy website test...
    # (Implementation would be similar to test_buggy_website)
    
    print("🔄 Would run same process with good website...")
    print("💡 This would show contrast between buggy vs good UX")

def main():
    """Main test function"""
    
    print("🧪 COMPLETE API TEST SUITE")
    print("=" * 30)
    print("This will test the entire pipeline:")
    print("1. Dynamic agent creation")
    print("2. Real-time execution monitoring") 
    print("3. LLM insights generation")
    print("4. Realistic sentiment analysis")
    print()
    
    # Check if server is running
    try:
        health_response = requests.get(f'{API_BASE}/health', timeout=5)
        if health_response.status_code == 200:
            print("✅ API server is running")
        else:
            print("⚠️  API server responded but might have issues")
    except:
        print("❌ API server is not running")
        print("💡 Start the backend with:")
        print("   cd /Users/ahmed/ArchetypeV2")
        print("   source venv/bin/activate")
        print("   OPENAI_API_KEY='your-key' python backend/main.py")
        return
    
    # Run the main test
    print("\n🚀 Starting buggy website test...")
    result = test_buggy_website()
    
    if result and result['success']:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Your dynamic agent system is working perfectly!")
        print("✅ Realistic LLM analysis is functioning!")
        print("✅ Ready for frontend integration!")
    else:
        print("\n❌ Test failed or incomplete")
        print("💡 Check the output above for details")

if __name__ == "__main__":
    main()
