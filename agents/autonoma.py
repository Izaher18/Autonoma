"""Autonoma — personal assistant that gets work done through specialists."""

import logging
from typing import Any, Optional

from core.base_agent import BaseAgent
from core.tool_registry import tool
from memory.memory_store import HybridMemory
from config.settings import Config

from .research_agent import ResearchAgent
from .code_assistant import CodeAssistantAgent
from .data_analyst import DataAnalystAgent

logger = logging.getLogger(__name__)


class AutonomaAgent(BaseAgent):
    """Personal helper: remembers context and delegates work to specialists.

    Talk to Autonoma the way you'd talk to a capable assistant. It can research,
    write code, and analyze data by calling specialist agents — you don't have to
    pick the right specialist yourself unless you want to.
    """

    def __init__(self, name: str = "Autonoma", memory: Optional[HybridMemory] = None, **kwargs):
        system_prompt = """You are Autonoma, the user's personal AI assistant.

You are not a chatbot that waits for perfect prompts. You are a helper that:
- Understands goals stated in everyday language
- Remembers what matters from past conversations (use remember / recall / search_memory)
- Gets work done by calling specialists when needed
- Explains what you're doing briefly, then delivers the result
- Asks one clarifying question only when you truly cannot proceed

Specialists available through your tools:
- ask_researcher — gather information, explain topics, synthesize findings
- ask_coder — write, debug, explain, or review code
- ask_analyst — statistics, trends, and data insights

Prefer doing the work over explaining how the user could do it. When a specialist
returns a result, summarize it clearly for the user. Be warm, concise, and direct —
like a sharp chief of staff, not a search engine."""

        super().__init__(name=name, system_prompt=system_prompt, **kwargs)

        self.memory = memory or HybridMemory(
            short_term_size=100,
            long_term_path=str(Config.MEMORY_DIR / "autonoma_memory.json"),
        )
        # Specialists get their own clients (same model settings). Do not share a
        # parent ScriptedLLM / response queue — that would steal turns mid-tool-call.
        specialist_kwargs = {
            "model": kwargs.get("model") or (self.llm.model if self.llm else None),
            "temperature": kwargs.get("temperature"),
            "use_llm": self.llm is not None,
        }
        self._researcher = ResearchAgent(name="Researcher", **specialist_kwargs)
        self._coder = CodeAssistantAgent(name="Coder", **specialist_kwargs)
        self._analyst = DataAnalystAgent(name="Analyst", **specialist_kwargs)

    def _run_specialist(self, agent: BaseAgent, task: str) -> str:
        """Run a specialist and surface its activity through this agent's events."""
        agent.on_event = self.on_event
        self.emit("specialist", specialist=agent.config.name, task=task[:120])
        try:
            return agent.execute(task)
        finally:
            agent.on_event = None

    @tool(description="Remember something important about the user or their goals")
    def remember(self, key: str, value: str, important: bool = True) -> str:
        """Store information in memory.

        Args:
            key: Short label for the memory
            value: What to remember
            important: Keep it in long-term memory if true
        """
        self.memory.remember(key, value, important=important)
        return f"Remembered {key}."

    @tool(description="Recall a specific memory by key")
    def recall(self, key: str) -> str:
        """Recall information from memory.

        Args:
            key: Memory key
        """
        value = self.memory.recall(key)
        return f"{key}: {value}" if value is not None else f"No memory for '{key}'."

    @tool(description="Search memories for something relevant")
    def search_memory(self, query: str, limit: int = 5) -> Any:
        """Search short-term and long-term memory.

        Args:
            query: What to look for
            limit: Max results
        """
        results = self.memory.search(query, limit=limit)
        return {"query": query, "results": results}

    @tool(description="Delegate research or information gathering to the research specialist")
    def ask_researcher(self, task: str) -> str:
        """Ask the research specialist to investigate something.

        Args:
            task: What to research
        """
        return self._run_specialist(self._researcher, task)

    @tool(description="Delegate coding, debugging, or explanation to the code specialist")
    def ask_coder(self, task: str) -> str:
        """Ask the code specialist for help.

        Args:
            task: Coding request
        """
        return self._run_specialist(self._coder, task)

    @tool(description="Delegate statistics, trends, or data analysis to the analyst specialist")
    def ask_analyst(self, task: str) -> str:
        """Ask the data analyst specialist.

        Args:
            task: Analysis request
        """
        return self._run_specialist(self._analyst, task)

    async def process_offline(self, user_input: str) -> str:
        """Simple offline helper when no API key is configured."""
        self.add_message("user", user_input)
        lower = user_input.lower()

        if any(w in lower for w in ("remember", "my name", "i like", "i prefer")):
            key = f"note_{len(self.memory.short_term.memory) + 1}"
            self.remember(key, user_input, important=True)
            response = (
                "Got it — I've saved that. Once an API key is configured I'll use "
                "it across future conversations automatically."
            )
        elif any(w in lower for w in ("code", "function", "python", "debug", "script")):
            response = self.ask_coder(user_input)
        elif any(w in lower for w in ("mean", "median", "trend", "data", "stat", "analy")):
            response = self.ask_analyst(user_input)
        elif any(w in lower for w in ("research", "what is", "explain", "tell me about")):
            response = self.ask_researcher(user_input)
        else:
            memories = self.search_memory(user_input, limit=3)
            hint = ""
            if memories["results"]:
                keys = [r.get("key") for r in memories["results"]]
                hint = f"\n\nI already know a few related things: {keys}"
            response = (
                "I'm Autonoma, your personal assistant. I can research topics, write code, "
                "analyze numbers, and remember what matters to you. Add an OpenAI or "
                "Anthropic key in `.env` for the full conversational experience, or try "
                'something like "research quantum computing" or "mean of 12, 18, 9".'
                f"{hint}"
            )

        self.add_message("assistant", response)
        return response
