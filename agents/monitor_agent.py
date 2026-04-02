"""
Monitor Agent - Real-time supplier risk detection using Tavily Search
"""

from config.agent_framework import DeterministicAgent
from config.groq_config import get_tavily_api_key

def create_monitor_agent(client=None, model_name: str = None):
    """
    Creates the Monitor Agent for external risk data collection
    
    Uses Tavily Search to detect adverse media and regulatory fines
    """
    
    tavily_key = get_tavily_api_key()
    
    def monitor_logic(context):
        """Execute search and return risk summary"""
        supplier_name = context.state.get('supplier_name', 'Unknown')
        
        if not tavily_key:
            fallback = f"External Risk Summary for {supplier_name}: No search API configured. Using deterministic assessment only."
            context.state['external_risks'] = fallback
            return fallback
        
        try:
            from tavily import TavilyClient
            tavily_client = TavilyClient(api_key=tavily_key)
            
            # Search for supplier risks
            query = f"{supplier_name} environmental violations fines regulatory issues"
            search_results = tavily_client.search(query, max_results=3)
            
            if search_results and 'results' in search_results:
                findings = []
                for result in search_results['results'][:3]:
                    findings.append(f"- {result.get('title', 'N/A')}: {result.get('content', 'N/A')[:200]}")
                
                if findings:
                    risk_summary = "\n".join(findings)
                    context.state['external_risks'] = risk_summary
                    return f"External Risk Summary for {supplier_name}:\n{risk_summary}"
            
            no_risk = f"No critical external risks detected for {supplier_name}"
            context.state['external_risks'] = no_risk
            return f"External Risk Summary for {supplier_name}: No critical external risks detected in recent news."
            
        except Exception as e:
            fallback = f"External Risk Summary for {supplier_name}: Search unavailable ({str(e)}). Proceeding with internal data only."
            context.state['external_risks'] = fallback
            return fallback
    
    return DeterministicAgent(name="MonitorAgent", logic_fn=monitor_logic)
