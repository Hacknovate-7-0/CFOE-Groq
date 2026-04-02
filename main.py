"""
Carbon Footprint Optimization Engine (CfoE)
Main entry point for running the multi-agent system using ADK framework
"""

import os
from dotenv import load_dotenv
from config.groq_config import get_groq_client

# Load environment variables
load_dotenv()

# Configure Groq client
client = get_groq_client()

# Import the root coordinator
from orchestrators.root_coordinator import create_root_coordinator

def run_audit(supplier_name: str, emissions: float, violations: int):
    """
    Run a complete ESG audit for a supplier using ADK multi-agent pipeline
    
    Args:
        supplier_name: Name of the supplier
        emissions: Annual CO2 emissions in tons
        violations: Number of regulatory violations
    """
    print(f"\n{'='*60}")
    print(f"Starting ESG Audit for: {supplier_name}")
    print(f"{'='*60}\n")
    
    # Create the root coordinator
    root_coordinator = create_root_coordinator(client)
    
    # Prepare input
    audit_input = f"""
    Conduct a comprehensive ESG audit for the following supplier:
    
    Supplier Name: {supplier_name}
    Annual CO2 Emissions: {emissions} tons
    Regulatory Violations: {violations}
    
    Please provide a complete risk assessment and recommendations.
    """
    
    # Run the multi-agent audit pipeline
    try:
        response = root_coordinator.generate_content(audit_input)
        
        print(f"\n{'='*60}")
        print("FINAL AUDIT REPORT")
        print(f"{'='*60}\n")
        print(response.text)
        print(f"\n{'='*60}\n")
        
        return response
        
    except Exception as e:
        print(f"Error during audit: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def main():
    """Main function with example usage"""
    
    print("\n" + "="*60)
    print("Carbon Footprint Optimization Engine (CfoE)")
    print("Multi-Agent ESG Compliance System (Groq + Llama)")
    print("="*60 + "\n")
    
    # Example 1: Low Risk Supplier
    print("\n--- Example 1: Low Risk Supplier ---")
    run_audit(
        supplier_name="GreenTech Solutions",
        emissions=500,
        violations=0
    )
    
    # Example 2: Moderate Risk Supplier
    print("\n--- Example 2: Moderate Risk Supplier ---")
    run_audit(
        supplier_name="StandardCorp Manufacturing",
        emissions=2500,
        violations=2
    )
    
    # Example 3: High Risk Supplier (triggers HITL)
    print("\n--- Example 3: High Risk Supplier ---")
    run_audit(
        supplier_name="PolluteCo Industries",
        emissions=8000,
        violations=5
    )

if __name__ == "__main__":
    main()
