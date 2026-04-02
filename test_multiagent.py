"""
Test script to verify multi-agent pipeline execution
"""

import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Configure API
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please add your API key.")

client = genai.Client(api_key=api_key)

# Import the coordinator
from orchestrators.root_coordinator import create_root_coordinator

def test_pipeline():
    """Test the multi-agent pipeline with a sample supplier"""
    
    print("\n" + "="*60)
    print("TESTING MULTI-AGENT PIPELINE")
    print("="*60 + "\n")
    
    # Create coordinator
    coordinator = create_root_coordinator(client)
    
    # Test input
    audit_input = """
    Conduct a comprehensive ESG audit for the following supplier:
    
    Supplier Name: TestCorp Industries
    Annual CO2 Emissions: 3500 tons
    Regulatory Violations: 3
    
    Please provide a complete risk assessment and recommendations.
    """
    
    # Run the pipeline
    print("Executing multi-agent audit pipeline...\n")
    response = coordinator.generate_content(audit_input)
    
    print("\n" + "="*60)
    print("PIPELINE TEST COMPLETE")
    print("="*60 + "\n")
    
    print("Final Report:")
    print("-" * 60)
    print(response.text)
    print("-" * 60)
    
    return response

if __name__ == "__main__":
    test_pipeline()
