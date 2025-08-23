"""
Minimal test without API key to verify setup
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.schemas import AgentInput, Persona, Viewport
from pathlib import Path


async def test_setup():
    print("Testing Agent Worker Setup...\n")
    
    # Test 1: Check dependencies
    print("1. Checking dependencies:")
    try:
        import playwright
        print("   ✓ Playwright installed")
    except ImportError:
        print("   ✗ Playwright not installed - run: pip install -r requirements.txt")
    
    try:
        import openai
        print("   ✓ OpenAI SDK installed")
    except ImportError:
        print("   ✗ OpenAI SDK not installed")
    
    # Test 2: Check directories
    print("\n2. Checking directories:")
    dirs = ["data", "static"]
    for dir_name in dirs:
        if Path(dir_name).exists():
            print(f"   ✓ {dir_name}/ exists")
        else:
            Path(dir_name).mkdir(exist_ok=True)
            print(f"   ✓ Created {dir_name}/")
    
    # Test 3: Test model creation
    print("\n3. Testing data models:")
    try:
        test_input = AgentInput(
            run_id="test_minimal",
            url="https://example.com",
            persona=Persona(name="Test", bio="Test user"),
            ux_question="Test question?",
            viewport=Viewport.MOBILE
        )
        print(f"   ✓ Created test input with run_id: {test_input.run_id}")
        print(f"   ✓ Viewport: {test_input.viewport.value}")
        print(f"   ✓ Step budget: {test_input.step_budget}")
    except Exception as e:
        print(f"   ✗ Model creation failed: {e}")
    
    # Test 4: Check API key
    print("\n4. Checking API key:")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_api_key_here":
        print("   ✓ API key is set")
    else:
        print("   ⚠ API key not set - add to .env file to run full demo")
    
    print("\n" + "="*50)
    print("Setup test complete!")
    print("\nNext steps:")
    print("1. Add your OPENAI_API_KEY to .env file")
    print("2. Run: python demo.py")
    print("3. Or run: python server.py (then test with curl)")


if __name__ == "__main__":
    asyncio.run(test_setup())