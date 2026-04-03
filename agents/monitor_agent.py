"""
Monitor Agent - Agentic RAG for real-time supplier risk detection
"""

from config.agent_framework import LLMAgent
from config.groq_config import get_tavily_api_key, MODEL_LLAMA

def create_monitor_agent(client, model_name: str = MODEL_LLAMA):
    """
    Creates the Monitor Agent with Agentic RAG capabilities
    
    Uses Tavily Search + LLM reasoning to analyze adverse media and regulatory fines
    """
    
    tavily_key = get_tavily_api_key()
    
    instruction = """You are the Monitor Agent responsible for conducting Agentic RAG (Retrieval-Augmented Generation) to assess external supplier risks.

Your task:
1. Analyze the supplier name and context provided
2. Review external search results about the supplier
3. Identify and assess:
   - Environmental violations and fines
   - Regulatory compliance issues
   - Safety incidents
   - Adverse media coverage
   - Reputational risks
4. Provide an intelligent risk assessment with severity levels

IMPORTANT:
- Ground your analysis in the actual search results provided
- Distinguish between high-severity and low-severity findings
- Identify patterns or recurring issues
- Assess credibility of sources
- Provide specific examples from search results
- Calculate an external_risk_score (0.0 to 0.3 scale) based on findings:
  * 0.0-0.1: No significant external risks
  * 0.1-0.2: Minor concerns or isolated incidents
  * 0.2-0.3: Serious adverse findings requiring attention

Output Format:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXTERNAL RISK MONITORING REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Supplier: [Name]
External Risk Score: [0.0-0.3]
Risk Level: [CRITICAL/MODERATE/LOW/NONE]

KEY FINDINGS:
[Analyze each search result with specific details]

RISK ASSESSMENT:
[Your intelligent analysis of severity, patterns, and implications]

RECOMMENDATIONS:
[Specific actions based on external findings]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Create custom execution wrapper for search integration
    class MonitorAgentWithSearch(LLMAgent):
        def execute(self, context, user_input):
            supplier_name = context.state.get('supplier_name', 'Unknown')
            
            # Perform search
            search_results_text = "No search results available."
            external_risk_score = 0.0
            
            if tavily_key:
                try:
                    from tavily import TavilyClient
                    tavily_client = TavilyClient(api_key=tavily_key)
                    
                    query = f"{supplier_name} environmental violations fines regulatory issues safety incidents"
                    search_results = tavily_client.search(query, max_results=5)
                    
                    if search_results and 'results' in search_results:
                        findings = []
                        for i, result in enumerate(search_results['results'][:5], 1):
                            title = result.get('title', 'N/A')
                            content = result.get('content', 'N/A')[:300]
                            url = result.get('url', 'N/A')
                            findings.append(f"\n[Result {i}]\nTitle: {title}\nContent: {content}\nSource: {url}")
                        
                        if findings:
                            search_results_text = "\n".join(findings)
                    else:
                        search_results_text = "No relevant news or incidents found in recent searches."
                        
                except Exception as e:
                    search_results_text = f"Search unavailable: {str(e)}"
            else:
                search_results_text = "Search API not configured. Unable to retrieve external data."
            
            # Build enhanced context message with search results
            enhanced_input = f"""Supplier Name: {supplier_name}

SEARCH RESULTS:
{search_results_text}

Please analyze these search results and provide a comprehensive external risk assessment for {supplier_name}.
Include an external_risk_score between 0.0 and 0.3 based on the severity of findings."""
            
            # Call parent LLM execution
            output = super().execute(context, enhanced_input)
            
            # Extract external_risk_score from LLM output
            import re
            score_match = re.search(r'External Risk Score:\s*([0-9.]+)', output)
            if score_match:
                try:
                    external_risk_score = float(score_match.group(1))
                    external_risk_score = max(0.0, min(0.3, external_risk_score))  # Clamp to 0.0-0.3
                except ValueError:
                    external_risk_score = 0.0
            
            # Store in context
            context.state['external_risks'] = output
            context.state['external_risk_score'] = external_risk_score
            context.state['search_results_raw'] = search_results_text
            
            return output
    
    return MonitorAgentWithSearch(
        name="MonitorAgent",
        client=client,
        model=model_name,
        instruction=instruction,
        max_tokens=2048
    )
