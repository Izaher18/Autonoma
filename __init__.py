"""Package initialization."""

__version__ = "0.1.0"
__author__ = "Agentic AI Project"
__license__ = "MIT"

from core import BaseAgent, AgentManager, ToolRegistry, tool
from agents import ResearchAgent, CodeAssistantAgent, DataAnalystAgent
from memory import HybridMemory, ShortTermMemory, LongTermMemory
from config import Config

__all__ = [
    "BaseAgent",
    "AgentManager",
    "ToolRegistry",
    "tool",
    "ResearchAgent",
    "CodeAssistantAgent",
    "DataAnalystAgent",
    "HybridMemory",
    "ShortTermMemory",
    "LongTermMemory",
    "Config",
]
