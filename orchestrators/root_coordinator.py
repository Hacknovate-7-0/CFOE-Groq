"""
Root Coordinator - Sequential orchestration using custom framework with Groq
"""

import re
from dataclasses import dataclass
from datetime import datetime

from config.agent_framework import SequentialOrchestrator, AgentContext
from config.groq_config import get_groq_client

from agents.monitor_agent import create_monitor_agent
from agents.calculation_agent import create_calculation_agent, calculate_carbon_score
from agents.policy_agent import create_policy_agent, enforce_policy_hitl
from agents.reporting_agent import create_reporting_agent


@dataclass
class CoordinatorResponse:
    """Response object compatible with main.py expectations."""
    text: str


class RootCoordinator:
    """
    Root coordinator using custom framework for multi-agent orchestration.
    
    Workflow:
    1. Monitor Agent - Gathers external risk data via Tavily Search
    2. Calculation Agent - Computes deterministic ESG risk scores
    3. Policy Agent - Enforces compliance policies with HITL
    4. Reporting Agent - Generates executive summary
    """

    def __init__(self, client):
        self.client = client

    @staticmethod
    def _extract_field(pattern: str, text: str, cast_type):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            return None
        raw = match.group(1).strip()
        try:
            return cast_type(raw)
        except (TypeError, ValueError):
            return None

    def _parse_audit_input(self, audit_input: str):
        supplier_name = self._extract_field(r"Supplier Name:\s*(.+)", audit_input, str)
        emissions = self._extract_field(r"Annual CO2 Emissions:\s*([0-9]+(?:\.[0-9]+)?)", audit_input, float)
        violations = self._extract_field(r"Regulatory Violations:\s*(\d+)", audit_input, int)

        if supplier_name is None or emissions is None or violations is None:
            raise ValueError("Could not parse supplier_name/emissions/violations from audit input.")

        return supplier_name, emissions, violations

    def generate_content(self, audit_input: str):
        """
        Orchestrates the complete multi-agent audit pipeline.
        """
        # Parse input
        supplier_name, emissions, violations = self._parse_audit_input(audit_input)
        
        print(f"\n{'='*60}")
        print(f"MULTI-AGENT PIPELINE EXECUTION")
        print(f"{'='*60}\n")
        
        try:
            # Create agents
            print("[1/5] Creating agents...")
            monitor_agent = create_monitor_agent(self.client)
            calculation_agent = create_calculation_agent()
            policy_agent = create_policy_agent(self.client)
            reporting_agent = create_reporting_agent(self.client)
            print("✓ All 4 agents created successfully\n")
            
            # Create orchestrator
            print("[2/5] Building audit pipeline...")
            orchestrator = SequentialOrchestrator([
                monitor_agent,
                calculation_agent,
                policy_agent,
                reporting_agent,
            ])
            print("✓ Sequential pipeline configured\n")
            
            # Initialize context with supplier data
            print("[3/5] Initializing context...")
            orchestrator.context.state["supplier_name"] = supplier_name
            orchestrator.context.state["emissions"] = emissions
            orchestrator.context.state["violations"] = violations
            print(f"✓ Context initialized with supplier data\n")
            
            # Run the pipeline
            print(f"[4/5] Executing multi-agent audit for {supplier_name}...\n")
            
            query = f"""Conduct a comprehensive ESG audit for supplier: {supplier_name}

Supplier Details:
- Name: {supplier_name}
- Annual CO2 Emissions: {emissions} tons
- Regulatory Violations: {violations}

Please execute the full audit workflow:
1. Search for external risk factors and recent news
2. Calculate ESG risk scores
3. Apply policy enforcement rules
4. Generate comprehensive audit report
"""
            
            result = orchestrator.run(query)
            
            print(f"[5/5] Pipeline completed successfully\n")
            
            # Extract final report
            report_text = result.get("final_output", "")
            
            # If report is empty or too short, use fallback
            if not report_text or len(report_text) < 200:
                print("⚠️  Generating fallback report...")
                report_text = self._generate_fallback_report(
                    supplier_name, emissions, violations, 
                    orchestrator.context.state
                )
            
            print(f"\n{'='*60}")
            print(f"PIPELINE COMPLETE - Report Generated")
            print(f"{'='*60}\n")
            
            return CoordinatorResponse(text=report_text)
            
        except Exception as e:
            print(f"\n❌ Error in pipeline: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback to deterministic report
            risk_data = calculate_carbon_score(emissions, violations)
            policy_data = enforce_policy_hitl(risk_data["risk_score"], supplier_name)
            
            fallback_report = self._generate_fallback_report(
                supplier_name, emissions, violations,
                {"ESG_RISK_SCORE": risk_data["risk_score"],
                 "risk_classification": risk_data["classification"],
                 "policy_decision_outcome": policy_data}
            )
            
            return CoordinatorResponse(text=fallback_report)

    def _generate_fallback_report(self, supplier_name, emissions, violations, state):
        """Generate comprehensive fallback report"""
        
        risk_score = state.get("ESG_RISK_SCORE", 0)
        classification = state.get("risk_classification", "Unknown")
        policy_outcome = state.get("policy_decision_outcome", {})
        external_risks = state.get("external_risks", "No external risk data available")
        
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine emissions analysis
        if emissions > 10000:
            emissions_analysis = f"The annual emissions of {emissions} tons CO2 are significantly high, indicating substantial environmental impact. This level requires immediate attention and aggressive reduction strategies."
        elif emissions > 5000:
            emissions_analysis = f"The annual emissions of {emissions} tons CO2 are moderately high, suggesting room for improvement in environmental practices and carbon reduction initiatives."
        else:
            emissions_analysis = f"The annual emissions of {emissions} tons CO2 are within acceptable ranges, though continuous monitoring and improvement efforts are recommended."
        
        # Determine violations analysis
        if violations >= 5:
            violations_analysis = f"With {violations} regulatory violations, this supplier demonstrates a concerning pattern of non-compliance. This poses significant legal and reputational risks that require immediate remediation."
        elif violations >= 2:
            violations_analysis = f"The {violations} regulatory violations indicate compliance challenges that need to be addressed through enhanced monitoring and corrective action plans."
        else:
            violations_analysis = f"With {violations} violation(s), the supplier shows relatively good compliance, though maintaining vigilance is essential."
        
        # Determine recommendations based on risk
        if classification == 'Critical Risk':
            recommendations = """   • IMMEDIATE: Suspend new orders pending compliance review
   • SHORT-TERM: Conduct on-site audit within 30 days
   • MEDIUM-TERM: Implement mandatory emissions reduction plan
   • LONG-TERM: Quarterly compliance reviews for 12 months
   • MONITORING: Weekly status reports until risk is mitigated
   • ESCALATION: Executive approval required for contract renewal"""
            final_rec = "Given the critical risk level, we recommend immediate suspension of new business pending a comprehensive compliance review. The supplier must demonstrate concrete improvement plans before partnership continuation can be considered."
        elif classification == 'Moderate Risk':
            recommendations = """   • SHORT-TERM: Request detailed emissions reduction roadmap
   • MEDIUM-TERM: Implement enhanced monitoring protocols
   • LONG-TERM: Bi-annual compliance audits
   • MONITORING: Monthly progress reports
   • SUPPORT: Provide ESG best practices guidance
   • REVIEW: Re-evaluate partnership terms in 6 months"""
            final_rec = "The partnership may continue with enhanced monitoring and clear improvement milestones. The supplier should provide quarterly progress reports on emissions reduction and compliance improvements."
        else:
            recommendations = """   • SHORT-TERM: Maintain current monitoring protocols
   • MEDIUM-TERM: Encourage continuous improvement initiatives
   • LONG-TERM: Annual compliance reviews
   • MONITORING: Standard quarterly reports
   • RECOGNITION: Consider for preferred supplier status
   • COLLABORATION: Share sustainability best practices"""
            final_rec = "The supplier demonstrates acceptable ESG performance. Continue partnership with standard monitoring protocols and encourage ongoing sustainability improvements."
        
        decision = policy_outcome.get('decision', 'N/A')
        reason = policy_outcome.get('reason', 'N/A')
        action = policy_outcome.get('recommended_action', 'N/A')
        human_approval = policy_outcome.get('human_approval_required', False)
        
        report_text = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUPPLIER AUDIT REPORT - {supplier_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. EXECUTIVE SUMMARY
   • Supplier Name: {supplier_name}
   • Audit Date: {current_date}
   • Risk Classification: {classification}
   • Overall Risk Score: {risk_score:.2f} / 1.00
   • Audit Status: {'CRITICAL' if risk_score >= 0.7 else 'FLAGGED' if risk_score >= 0.4 else 'PASSED'}

   Summary: This comprehensive ESG audit evaluates {supplier_name} across 
   environmental impact, regulatory compliance, and external risk factors. 
   The supplier has been classified as {classification} based on 
   emissions data and violation history. {reason}

2. ENVIRONMENTAL IMPACT ASSESSMENT
   • Annual CO2 Emissions: {emissions} tons
   • Emissions Score: {state.get('emissions_score', 'N/A')} / 1.00
   • Industry Benchmark: {'Above average' if emissions > 5000 else 'Within normal range'}
   
   Analysis: {emissions_analysis}

3. REGULATORY COMPLIANCE REVIEW
   • Regulatory Violations: {violations} incidents
   • Violations Score: {state.get('violations_score', 'N/A')} / 1.00
   • Compliance Status: {'CRITICAL' if violations >= 5 else 'NON-COMPLIANT' if violations >= 2 else 'COMPLIANT'}
   
   Analysis: {violations_analysis}

4. EXTERNAL RISK FACTORS
   {external_risks}

5. POLICY ENFORCEMENT OUTCOME
   • Decision: {decision}
   • Human Approval Required: {'YES' if human_approval else 'NO'}
   • Recommended Action: {action}
   
   Rationale: {reason}

6. RISK MITIGATION RECOMMENDATIONS
{recommendations}

7. FINAL RECOMMENDATION
   {final_rec} Key success metrics include: emissions reduction 
   trajectory, violation remediation progress, and implementation of recommended 
   corrective actions. Regular monitoring will ensure continuous improvement and 
   alignment with our ESG standards.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Report Generated: {current_date}
Report Source: Deterministic Fallback
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REFERENCES & RESOURCES:
• ESG Reporting Standards: https://www.globalreporting.org/standards/
• Carbon Disclosure Project: https://www.cdp.net/
• Science Based Targets Initiative: https://sciencebasedtargets.org/
• EPA Compliance Resources: https://www.epa.gov/compliance
• ISO 14001 Environmental Management: https://www.iso.org/iso-14001-environmental-management.html

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return report_text


def create_root_coordinator(client):
    """
    Creates the Root Coordinator using custom framework
    
    Workflow:
    1. Monitor Agent: Gathers external risk data via search
    2. Calculation Agent: Deterministic risk scoring
    3. Policy Agent: HITL enforcement
    4. Reporting Agent: Executive summary
    """
    
    return RootCoordinator(client)
