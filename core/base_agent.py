"""Base agent class that all agents inherit from."""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Callable
from abc import ABC
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from pydantic import BaseModel, Field

from config.settings import Config
from .llm import LLMClient, ToolCall, create_llm
from .tool_registry import tool_schema

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
    model: Optional[str] = None
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
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        llm: Optional[LLMClient] = None,
        use_llm: bool = True,
    ):
        """Initialize the base agent.

        Args:
            name: Name of the agent
            model: LLM model to use (defaults to DEFAULT_MODEL, or a default for
                whichever provider has an API key configured)
            temperature: Temperature for generation (ignored by Anthropic models)
            system_prompt: Custom system prompt
            llm: Pre-built LLM client; overrides ``model``
            use_llm: Set False to force offline mode even when API keys are set
        """
        if llm is None and use_llm:
            llm = create_llm(model)
        self.llm = llm
        self.config = AgentConfig(
            name=name,
            model=llm.model if llm else model,
            temperature=Config.DEFAULT_TEMPERATURE if temperature is None else temperature,
            max_tokens=Config.MAX_TOKENS,
            max_iterations=Config.MAX_ITERATIONS,
            system_prompt=system_prompt,
        )
        self.conversation_history: List[Message] = []
        self.tools: Dict[str, Callable] = {}
        self.state: Dict[str, Any] = {}

        # Register tools from methods decorated with @tool
        self._register_tools()

        mode = f"model {self.llm.model}" if self.llm else "offline"
        logger.info(f"Initialized agent: {name} ({mode})")

    def _register_tools(self):
        """Register methods decorated with @tool as available tools."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, "_is_tool"):
                self.tools[attr_name] = attr
                logger.debug(f"Registered tool: {attr_name}")

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation history.

        Args:
            role: Role of the message sender (user, assistant, system)
            content: Message content
            metadata: Optional metadata
        """
        message = Message(role=role, content=content, metadata=metadata or {})
        self.conversation_history.append(message)

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent.

        Returns:
            System prompt string
        """
        if self.config.system_prompt:
            return self.config.system_prompt

        tools_desc = self._get_tools_description()
        return f"""You are {self.config.name}, an AI agent designed to help users \
with various tasks.

You have access to the following tools:
{tools_desc}

Call a tool whenever it helps you answer accurately. When you have the answer, \
reply to the user directly.

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
            desc = getattr(tool_func, "_tool_description", "No description available")
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
            raise ValueError(
                f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
            )

        logger.info(f"Calling tool: {tool_name} with input: {tool_input}")

        try:
            result = self.tools[tool_name](**tool_input)
            logger.info(f"Tool {tool_name} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            raise

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get JSON-schema definitions for the tools the model may call."""
        return [
            tool_schema(name, func)
            for name, func in self.tools.items()
            if getattr(func, "_expose_to_llm", True)
        ]

    async def process(self, user_input: str) -> str:
        """Process user input and generate a response.

        Runs the LLM tool-calling loop when a model is configured, otherwise falls
        back to ``process_offline``. Subclasses may override this entirely.

        Args:
            user_input: User's input message

        Returns:
            Agent's response
        """
        if self.llm is None:
            return await self.process_offline(user_input)
        return await self.run_llm(user_input)

    async def process_offline(self, user_input: str) -> str:
        """Respond without an LLM. Override to provide a scripted workflow."""
        raise NotImplementedError(
            f"{type(self).__name__} has no offline mode. "
            "Set OPENAI_API_KEY or ANTHROPIC_API_KEY to use an LLM."
        )

    async def run_llm(self, user_input: str) -> str:
        """Let the model answer, calling tools until it gives a final reply.

        Prior user/assistant turns are sent as context; tool exchanges from this
        run are not kept in ``conversation_history``.
        """
        self.add_message("user", user_input)
        messages: List[Dict[str, Any]] = [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
            if msg.role in ("user", "assistant")
        ]
        tools = self.get_tool_schemas()
        exposed = {schema["name"] for schema in tools}
        system = self.get_system_prompt()
        tools_used: List[str] = []

        for _ in range(self.config.max_iterations):
            response = await asyncio.to_thread(
                self.llm.chat,
                system,
                messages,
                tools or None,
                self.config.temperature,
                self.config.max_tokens,
            )
            if not response.tool_calls:
                self.add_message("assistant", response.text, {"tools_used": tools_used})
                return response.text

            messages.append(
                {"role": "assistant", "content": response.text, "tool_calls": response.tool_calls}
            )
            for call in response.tool_calls:
                tools_used.append(call.name)
                messages.append(self._run_tool_call(call, exposed))

        logger.warning(
            f"{self.config.name} hit max_iterations={self.config.max_iterations} "
            "without a final answer"
        )
        answer = (
            f"Stopped after {self.config.max_iterations} tool-calling steps "
            "without reaching a final answer."
        )
        self.add_message("assistant", answer, {"tools_used": tools_used})
        return answer

    def _run_tool_call(self, call: ToolCall, exposed: set) -> Dict[str, Any]:
        """Execute one model-requested tool call and package the result for the model."""
        try:
            if call.name not in exposed:
                raise ValueError(f"Unknown tool '{call.name}'. Available: {sorted(exposed)}")
            result = self.call_tool(call.name, call.arguments)
            content = result if isinstance(result, str) else json.dumps(result, default=str)
            is_error = False
        except Exception as e:
            content = f"Error: {e}"
            is_error = True
        return {
            "role": "tool",
            "tool_call_id": call.id,
            "content": content,
            "is_error": is_error,
        }

    def execute(self, task: str) -> str:
        """Synchronous wrapper for process method.

        Safe to call from inside a running event loop (e.g. Jupyter or async code),
        where ``asyncio.run`` would otherwise raise.

        Args:
            task: Task description

        Returns:
            Execution result
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.process(task))

        with ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, self.process(task)).result()

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
            "state": self.state,
        }

        with open(filepath, "w") as f:
            json.dump(state_data, f, indent=2, default=str)

        logger.info(f"Saved agent state to {filepath}")

    def load_state(self, filepath: str):
        """Load agent state from a file.

        Args:
            filepath: Path to load the state from
        """
        with open(filepath, "r") as f:
            state_data = json.load(f)

        if "config" in state_data:
            self.config = AgentConfig(**state_data["config"])
        self.conversation_history = [
            Message(
                **{
                    **msg,
                    "timestamp": (
                        datetime.fromisoformat(msg["timestamp"])
                        if isinstance(msg.get("timestamp"), str)
                        else msg.get("timestamp", datetime.now())
                    ),
                }
            )
            for msg in state_data.get("conversation_history", [])
        ]
        self.state = state_data.get("state", {})

        logger.info(f"Loaded agent state from {filepath}")
