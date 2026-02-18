"""Base agent class that all agents inherit from."""

import json
import logging
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """Represents a message in the conversation."""
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    name: str
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 4096
    max_iterations: int = 10
    enable_memory: bool = True
    system_prompt: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(
        self,
        name: str,
        model: str = "gpt-4-turbo-preview",
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ):
        """Initialize the base agent.
        
        Args:
            name: Name of the agent
            model: LLM model to use
            temperature: Temperature for generation
            system_prompt: Custom system prompt
        """
        self.config = AgentConfig(
            name=name,
            model=model,
            temperature=temperature,
            system_prompt=system_prompt
        )
        self.conversation_history: List[Message] = []
        self.tools: Dict[str, Callable] = {}
        self.state: Dict[str, Any] = {}
        
        # Register tools from methods decorated with @tool
        self._register_tools()
        
        logger.info(f"Initialized agent: {name}")
    
    def _register_tools(self):
        """Register methods decorated with @tool as available tools."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_is_tool'):
                self.tools[attr_name] = attr
                logger.debug(f"Registered tool: {attr_name}")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation history.
        
        Args:
            role: Role of the message sender (user, assistant, system)
            content: Message content
            metadata: Optional metadata
        """
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.conversation_history.append(message)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent.
        
        Returns:
            System prompt string
        """
        if self.config.system_prompt:
            return self.config.system_prompt
        
        tools_desc = self._get_tools_description()
        return f"""You are {self.config.name}, an AI agent designed to help users with various tasks.

You have access to the following tools:
{tools_desc}

When you need to use a tool, respond with a JSON object in this format:
{{
    "thought": "Your reasoning about what to do",
    "tool": "tool_name",
    "tool_input": {{"param": "value"}}
}}

When you have a final answer, respond with:
{{
    "thought": "Your reasoning",
    "final_answer": "Your answer to the user"
}}

Always think step by step and explain your reasoning."""
    
    def _get_tools_description(self) -> str:
        """Get a description of all available tools.
        
        Returns:
            Formatted string describing all tools
        """
        if not self.tools:
            return "No tools available."
        
        descriptions = []
        for name, tool_func in self.tools.items():
            desc = getattr(tool_func, '_tool_description', 'No description available')
            descriptions.append(f"- {name}: {desc}")
        
        return "\n".join(descriptions)
    
    def call_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Call a tool by name with given input.
        
        Args:
            tool_name: Name of the tool to call
            tool_input: Input parameters for the tool
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}")
        
        logger.info(f"Calling tool: {tool_name} with input: {tool_input}")
        
        try:
            result = self.tools[tool_name](**tool_input)
            logger.info(f"Tool {tool_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            raise
    
    @abstractmethod
    async def process(self, user_input: str) -> str:
        """Process user input and generate a response.
        
        This method should be implemented by each specific agent.
        
        Args:
            user_input: User's input message
            
        Returns:
            Agent's response
        """
        pass
    
    def execute(self, task: str) -> str:
        """Synchronous wrapper for process method.
        
        Args:
            task: Task description
            
        Returns:
            Execution result
        """
        import asyncio
        return asyncio.run(self.process(task))
    
    def reset(self):
        """Reset the agent's conversation history and state."""
        self.conversation_history = []
        self.state = {}
        logger.info(f"Reset agent: {self.config.name}")
    
    def save_state(self, filepath: str):
        """Save agent state to a file.
        
        Args:
            filepath: Path to save the state
        """
        state_data = {
            "config": self.config.model_dump(),
            "conversation_history": [msg.model_dump() for msg in self.conversation_history],
            "state": self.state
        }
        
        with open(filepath, 'w') as f:
            json.dump(state_data, f, indent=2, default=str)
        
        logger.info(f"Saved agent state to {filepath}")
    
    def load_state(self, filepath: str):
        """Load agent state from a file.
        
        Args:
            filepath: Path to load the state from
        """
        with open(filepath, 'r') as f:
            state_data = json.load(f)
        
        if "config" in state_data:
            self.config = AgentConfig(**state_data["config"])
        self.conversation_history = [
            Message(**{**msg, "timestamp": datetime.fromisoformat(msg["timestamp"]) if isinstance(msg.get("timestamp"), str) else msg.get("timestamp", datetime.now())})
            for msg in state_data.get("conversation_history", [])
        ]
        self.state = state_data.get("state", {})
        
        logger.info(f"Loaded agent state from {filepath}")
