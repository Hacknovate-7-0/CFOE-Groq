"""
Custom Agent Framework - Lightweight replacement for Google ADK
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field


@dataclass
class AgentContext:
    """Context passed between agents containing session state"""
    state: Dict[str, Any] = field(default_factory=dict)
    messages: List[str] = field(default_factory=list)


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def execute(self, context: AgentContext, user_input: str) -> str:
        """
        Execute agent logic
        
        Args:
            context: Shared context with state
            user_input: Input message
            
        Returns:
            Agent output as string
        """
        pass


class LLMAgent(BaseAgent):
    """Agent that uses LLM for reasoning"""
    
    def __init__(
        self,
        name: str,
        client: Any,
        model: str,
        instruction: str,
        tools: Optional[List[Callable]] = None,
        output_key: Optional[str] = None,
        max_tokens: int = 8192
    ):
        super().__init__(name)
        self.client = client
        self.model = model
        self.instruction = instruction
        self.tools = tools or []
        self.output_key = output_key
        self.max_tokens = max_tokens
    
    def execute(self, context: AgentContext, user_input: str) -> str:
        """Execute LLM agent with tools"""
        
        # Build messages
        messages = [
            {"role": "system", "content": self.instruction},
            {"role": "user", "content": self._build_context_message(context, user_input)}
        ]
        
        # Call LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            output = response.choices[0].message.content
            
            # Store in context if output_key specified
            if self.output_key:
                context.state[self.output_key] = output
            
            return output
            
        except Exception as e:
            error_msg = f"Error in {self.name}: {str(e)}"
            print(f"⚠️  {error_msg}")
            return error_msg
    
    def _build_context_message(self, context: AgentContext, user_input: str) -> str:
        """Build message with context state"""
        context_info = "\n".join([f"{k}: {v}" for k, v in context.state.items()])
        return f"Context:\n{context_info}\n\nTask:\n{user_input}"


class DeterministicAgent(BaseAgent):
    """Agent that executes deterministic logic without LLM"""
    
    def __init__(self, name: str, logic_fn: Callable):
        super().__init__(name)
        self.logic_fn = logic_fn
    
    def execute(self, context: AgentContext, user_input: str) -> str:
        """Execute deterministic logic"""
        try:
            return self.logic_fn(context)
        except Exception as e:
            error_msg = f"Error in {self.name}: {str(e)}"
            print(f"⚠️  {error_msg}")
            return error_msg


class SequentialOrchestrator:
    """Orchestrates multiple agents in sequence"""
    
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents
        self.context = AgentContext()
    
    def run(self, initial_input: str) -> Dict[str, Any]:
        """
        Run all agents sequentially
        
        Args:
            initial_input: Initial user input
            
        Returns:
            Dict with final output and context state
        """
        current_input = initial_input
        outputs = []
        
        print(f"\n{'='*60}")
        print(f"SEQUENTIAL ORCHESTRATOR - {len(self.agents)} Agents")
        print(f"{'='*60}\n")
        
        for i, agent in enumerate(self.agents, 1):
            print(f"[{i}/{len(self.agents)}] Executing {agent.name}...")
            
            output = agent.execute(self.context, current_input)
            outputs.append({
                "agent": agent.name,
                "output": output
            })
            
            print(f"✓ {agent.name} completed")
            print(f"  Output preview: {output[:150]}...\n")
            
            # Pass output to next agent
            current_input = output
        
        print(f"{'='*60}")
        print("All agents completed successfully")
        print(f"{'='*60}\n")
        
        return {
            "final_output": outputs[-1]["output"] if outputs else "",
            "all_outputs": outputs,
            "context": self.context.state
        }
