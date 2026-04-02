"""
Carbon Footprint Optimization Engine (CfoE)
Simplified version using Google GenAI API correctly
"""

import os
from dotenv import load_dotenv
from config.groq_config import get_groq_client

# Load environment variables
load_dotenv()

# Configure Groq client
client = get_groq_client()

def calculate_carbon_score(emissions: float, violations: int) -> dict:
    """
    Deterministic ESG risk score calculation
    
    Args:
        emissions: Annual CO2 emissions in tons
        violations: Number of regulatory violations
        
    Returns:
        dict with risk_score (0.0-1.0) and classification
    """
    
    # Emissions scoring (0-0.5 range)
    if emissions < 1000:
        emissions_score = 0.1
    elif emissions < 3000:
        emissions_score = 0.25
    elif emissions < 5000:
        emissions_score = 0.35
    else:
        emissions_score = 0.5
    
    # Violations scoring (0-0.5 range)
    violations_score = min(violations * 0.1, 0.5)
    
    # Total risk score
    risk_score = emissions_score + violations_score
    
    # Classification
    if risk_score < 0.4:
        classification = "Low Risk"
    elif risk_score < 0.8:
        classification = "Moderate Risk"
    else:
        classification = "Critical Risk"
    
    return {
        "risk_score": round(risk_score, 2),
        "classification": classification,
        "emissions_score": round(emissions_score, 2),
        "violations_score": round(violations_score, 2)
    }

def enforce_policy_hitl(risk_score: float, supplier_name: str) -> dict:
    """
    Enforce compliance policy with Human-in-the-Loop for critical risks
    
    Args:
        risk_score: ESG risk score (0.0-1.0)
        supplier_name: Name of the supplier
        
    Returns:
        dict with policy decision and human_approval_required flag
    """
    
    if risk_score >= 0.8:
        return {
            "decision": "PAUSE - Human Approval Required",
            "human_approval_required": True,
            "reason": f"Critical risk detected (score: {risk_score}). Manual review mandatory.",
            "recommended_action": "Suspend supplier relationship pending investigation"
        }
    elif risk_score >= 0.4:
        return {
            "decision": "FLAGGED - Enhanced Monitoring",
            "human_approval_required": False,
            "reason": f"Moderate risk detected (score: {risk_score}). Increased oversight recommended.",
            "recommended_action": "Implement quarterly audits and improvement plan"
        }
    else:
        return {
            "decision": "APPROVED - Standard Monitoring",
            "human_approval_required": False,
            "reason": f"Low risk detected (score: {risk_score}). Continue normal operations.",
            "recommended_action": "Maintain annual audit schedule"
        }

def run_audit(supplier_name: str, emissions: float, violations: int):
    """
    Run a complete ESG audit for a supplier
    
    Args:
        supplier_name: Name of the supplier
        emissions: Annual CO2 emissions in tons
        violations: Number of regulatory violations
    """
    print(f"\n{'='*60}")
    print(f"Starting ESG Audit for: {supplier_name}")
    print(f"{'='*60}\n")
    
    # Phase 1: Calculate Risk Score
    print("Phase 1: Calculating ESG Risk Score...")
    risk_data = calculate_carbon_score(emissions, violations)
    print(f"  ✓ Risk Score: {risk_data['risk_score']}")
    print(f"  ✓ Classification: {risk_data['classification']}")
    print(f"  ✓ Emissions Score: {risk_data['emissions_score']}")
    print(f"  ✓ Violations Score: {risk_data['violations_score']}\n")
    
    # Phase 2: Policy Enforcement
    print("Phase 2: Enforcing Compliance Policy...")
    policy_decision = enforce_policy_hitl(risk_data['risk_score'], supplier_name)
    print(f"  ✓ Decision: {policy_decision['decision']}")
    print(f"  ✓ Reason: {policy_decision['reason']}")
    print(f"  ✓ Recommended Action: {policy_decision['recommended_action']}\n")
    
    # Phase 3: Generate Report with AI
    print("Phase 3: Generating Executive Report with AI...\n")
    
    prompt = f"""
    Generate a comprehensive ESG audit report for the following supplier:
    
    SUPPLIER INFORMATION:
    - Name: {supplier_name}
    - Annual CO2 Emissions: {emissions} tons
    - Regulatory Violations: {violations}
    
    RISK ASSESSMENT:
    - Risk Score: {risk_data['risk_score']} / 1.00
    - Classification: {risk_data['classification']}
    - Emissions Score: {risk_data['emissions_score']}
    - Violations Score: {risk_data['violations_score']}
    
    POLICY DECISION:
    - Decision: {policy_decision['decision']}
    - Human Approval Required: {policy_decision['human_approval_required']}
    - Reason: {policy_decision['reason']}
    - Recommended Action: {policy_decision['recommended_action']}
    
    You MUST write a detailed, multi-section report covering ALL of the following sections in full:
    1. Executive Summary (3-4 sentences)
    2. Key Findings (at least 4 bullet points)
    3. Risk Analysis (detailed breakdown of emissions and violations impact)
    4. Compliance Status (regulatory standing and gaps)
    5. Recommended Actions (at least 4 specific, actionable items)
    6. Next Steps (timeline and ownership)

    Each section must be thorough. Do not summarize or truncate any section.
    
    IMPORTANT: End the report with a REFERENCES & RESOURCES section containing:
    • ESG Reporting Standards: https://www.globalreporting.org/standards/
    • Carbon Disclosure Project: https://www.cdp.net/
    • Science Based Targets Initiative: https://sciencebasedtargets.org/
    • EPA Compliance Resources: https://www.epa.gov/compliance
    • ISO 14001 Environmental Management: https://www.iso.org/iso-14001-environmental-management.html
    """
    
    try:
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {"role": "system", "content": "You are a senior ESG compliance analyst. Always produce detailed, structured, multi-section audit reports. Never truncate or summarize sections. Each section must be fully elaborated."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8192,
            temperature=0.7
        )
        
        print(f"{'='*60}")
        print("EXECUTIVE AUDIT REPORT")
        print(f"{'='*60}\n")
        print(response.choices[0].message.content)
        print(f"\n{'='*60}\n")
        
        return response
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        print("\nFalling back to basic report...\n")
        
        # Fallback basic report
        print(f"{'='*60}")
        print("EXECUTIVE AUDIT REPORT")
        print(f"{'='*60}\n")
        print(f"Supplier: {supplier_name}")
        print(f"Risk Score: {risk_data['risk_score']} ({risk_data['classification']})")
        print(f"Decision: {policy_decision['decision']}")
        print(f"Action: {policy_decision['recommended_action']}")
        print(f"\n{'='*60}\n")

def main():
    """Main function with example usage"""
    
    print("\n" + "="*60)
    print("Carbon Footprint Optimization Engine (CfoE)")
    print("Multi-Agent ESG Compliance System")
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
