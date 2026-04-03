"""
Calculation Agent - Deterministic ESG risk scoring
"""

from config.agent_framework import DeterministicAgent

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
    
    # Classification - aligned with HITL threshold at 0.70
    if risk_score >= 0.7:
        classification = "Critical Risk"
    elif risk_score >= 0.4:
        classification = "Moderate Risk"
    else:
        classification = "Low Risk"
    
    return {
        "risk_score": round(risk_score, 2),
        "classification": classification,
        "emissions_score": round(emissions_score, 2),
        "violations_score": round(violations_score, 2)
    }

def calculate_carbon_score_logic(context):
    """Execute carbon score calculation from context"""
    emissions = context.state.get('emissions', 0)
    violations = context.state.get('violations', 0)
    external_risk_score = context.state.get('external_risk_score', 0.0)
    
    result = calculate_carbon_score(emissions, violations)
    
    # Integrate external risk score (0.0-0.3 range)
    base_risk_score = result["risk_score"]
    adjusted_risk_score = min(1.0, base_risk_score + external_risk_score)
    
    # Reclassify based on adjusted score
    if adjusted_risk_score >= 0.7:
        adjusted_classification = "Critical Risk"
    elif adjusted_risk_score >= 0.4:
        adjusted_classification = "Moderate Risk"
    else:
        adjusted_classification = "Low Risk"
    
    # Store in context
    context.state["base_risk_score"] = base_risk_score
    context.state["ESG_RISK_SCORE"] = adjusted_risk_score
    context.state["risk_classification"] = adjusted_classification
    context.state["emissions_score"] = result["emissions_score"]
    context.state["violations_score"] = result["violations_score"]
    context.state["external_risk_score"] = external_risk_score
    
    external_impact = "" if external_risk_score == 0 else f"\n  • External Risk Score: {external_risk_score:.2f}\n  • Base Score: {base_risk_score} → Adjusted Score: {adjusted_risk_score:.2f}"
    
    output = f"""ESG Risk Score Calculation Complete:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input Data:
  • Emissions: {emissions} tons
  • Violations: {violations}{external_impact}

Risk Components:
  • Emissions Score: {result['emissions_score']}
  • Violations Score: {result['violations_score']}
  • External Risk Score: {external_risk_score:.2f}

FINAL ESG RISK SCORE: {adjusted_risk_score:.2f}
CLASSIFICATION: {adjusted_classification}
{'🚨 CRITICAL - Requires Human Review' if adjusted_risk_score >= 0.70 else '🟢 AUTO-APPROVED'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    return output

def create_calculation_agent(emissions: float = None, violations: int = None):
    """
    Creates the Calculation Agent with deterministic scoring
    
    Args:
        emissions: Annual CO2 emissions in tons (optional, can be in context)
        violations: Number of regulatory violations (optional, can be in context)
    """
    
    return DeterministicAgent(
        name="CalculationAgent",
        logic_fn=calculate_carbon_score_logic
    )
