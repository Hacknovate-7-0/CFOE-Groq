"""
Simple test script to verify CfoE setup
"""

import os
from dotenv import load_dotenv

def test_setup():
    """Test that everything is configured correctly"""
    
    print("Testing CfoE Setup...")
    print("-" * 50)
    
    # Test 1: Check .env file
    print("\n1. Checking .env file...")
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("   ❌ GOOGLE_API_KEY not found in .env file")
        print("   → Please add your API key to the .env file")
        return False
    elif api_key == "your_api_key_here":
        print("   ❌ GOOGLE_API_KEY not configured")
        print("   → Please replace 'your_api_key_here' with your actual API key")
        return False
    else:
        print(f"   ✅ API key found (starts with: {api_key[:10]}...)")
    
    # Test 2: Check imports
    print("\n2. Checking imports...")
    try:
        from google import genai
        print("   ✅ google-genai imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import google-genai: {e}")
        print("   → Run: pip install -r requirements.txt")
        return False
    
    try:
        from agents.monitor_agent import create_monitor_agent
        from agents.calculation_agent import create_calculation_agent
        from agents.policy_agent import create_policy_agent
        from agents.reporting_agent import create_reporting_agent
        print("   ✅ All agents imported successfully")
    except ImportError as e:
        print(f"   ❌ Failed to import agents: {e}")
        return False
    
    # Test 3: Test calculation function
    print("\n3. Testing calculation function...")
    try:
        from agents.calculation_agent import calculate_carbon_score
        result = calculate_carbon_score(emissions=1500, violations=2)
        print(f"   ✅ Calculation works: Risk Score = {result['risk_score']}")
    except Exception as e:
        print(f"   ❌ Calculation failed: {e}")
        return False
    
    # Test 4: Test policy function
    print("\n4. Testing policy function...")
    try:
        from agents.policy_agent import enforce_policy_hitl
        result = enforce_policy_hitl(risk_score=0.5, supplier_name="Test Corp")
        print(f"   ✅ Policy enforcement works: {result['decision']}")
    except Exception as e:
        print(f"   ❌ Policy enforcement failed: {e}")
        return False
    
    # Test 5: Test API connection
    print("\n5. Testing API connection...")
    try:
        from google.genai import types
        client = genai.Client(api_key=api_key)
        print("   ✅ API client created successfully")
    except Exception as e:
        print(f"   ❌ API connection failed: {e}")
        print("   → Check your API key and internet connection")
        return False
    
    print("\n" + "="*50)
    print("✅ All tests passed! You're ready to run main.py")
    print("="*50)
    print("\nRun the main script with:")
    print("  python main.py")
    
    return True

if __name__ == "__main__":
    test_setup()
