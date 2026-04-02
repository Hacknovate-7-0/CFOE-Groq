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
    
    result = calculate_carbon_score(emissions, violations)
    
    # Store in context
    context.state["ESG_RISK_SCORE"] = result["risk_score"]
    context.state["risk_classification"] = result["classification"]
    context.state["emissions_score"] = result["emissions_score"]
    context.state["violations_score"] = result["violations_score"]
    
    output = f"""ESG Risk Score Calculation Complete:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input Data:
  • Emissions: {emissions} tons
  • Violations: {violations}

Risk Components:
  • Emissions Score: {result['emissions_score']}
  • Violations Score: {result['violations_score']}

FINAL ESG RISK SCORE: {result['risk_score']}
CLASSIFICATION: {result['classification']}
{'🚨 CRITICAL - Requires Human Review' if result['risk_score'] >= 0.70 else '🟢 AUTO-APPROVED'}
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
