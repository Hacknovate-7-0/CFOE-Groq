"""
Policy Agent - Human-in-the-Loop compliance enforcement
"""

from config.agent_framework import LLMAgent, DeterministicAgent
from config.groq_config import MODEL_LLAMA

def enforce_policy_hitl(risk_score: float, supplier_name: str) -> dict:
    """
    Enforce compliance policy with Human-in-the-Loop for critical risks
    
    Args:
        risk_score: ESG risk score (0.0-1.0)
        supplier_name: Name of the supplier
        
    Returns:
        dict with policy decision and human_approval_required flag
    """
    
    # CRITICAL: >= 0.70 requires human approval (aligned with Critical Risk classification)
    if risk_score >= 0.7:
        return {
            "decision": "ESCALATE_TO_HUMAN_REVIEW",
            "human_approval_required": True,
            "reason": f"Risk score {risk_score} exceeds critical threshold (0.70). Manual review mandatory.",
            "recommended_action": "Suspend new orders pending compliance review and executive approval"
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

def policy_logic(context):
    """Execute policy enforcement logic"""
    risk_score = context.state.get('ESG_RISK_SCORE', 0)
    supplier_name = context.state.get('supplier_name', 'Unknown')
    
    policy_result = enforce_policy_hitl(risk_score, supplier_name)
    
    # Store in context
    context.state['policy_decision_outcome'] = policy_result
    
    output = f"""Policy Enforcement Complete:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Supplier: {supplier_name}
Risk Score: {risk_score}

DECISION: {policy_result['decision']}
Human Approval Required: {'YES' if policy_result['human_approval_required'] else 'NO'}

Reason: {policy_result['reason']}
Recommended Action: {policy_result['recommended_action']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    return output

def create_policy_agent(client=None, model_name: str = MODEL_LLAMA):
    """
    Creates the Policy Agent with HITL enforcement
    """
    
    return DeterministicAgent(
        name="PolicyAgent",
        logic_fn=policy_logic
    )
