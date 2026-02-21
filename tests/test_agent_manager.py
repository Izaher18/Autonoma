
"""Tests for agent manager functionality."""

import pytest
from core.agent_manager import AgentManager
from core.base_agent import BaseAgent
from core.tool_registry import tool


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def __init__(self, name="MockAgent"):
        super().__init__(name=name)
    
    async def process(self, user_input: str) -> str:
        """Process mock input."""
        return f"{self.config.name} processed: {user_input}"


def test_agent_manager_initialization():
    """Test agent manager initialization."""
    manager = AgentManager(max_workers=3)
    assert manager.max_workers == 3
    assert len(manager.agents) == 0


def test_add_agent():
    """Test adding an agent."""
    manager = AgentManager()
    agent = MockAgent(name="Agent1")
    manager.add_agent(agent)
    
    assert "Agent1" in manager.agents
    assert manager.get_agent("Agent1") is agent


def test_add_duplicate_agent():
    """Test adding duplicate agent raises error."""
    manager = AgentManager()
    agent1 = MockAgent(name="Agent1")
    agent2 = MockAgent(name="Agent1")
    
    manager.add_agent(agent1)
    with pytest.raises(ValueError):
        manager.add_agent(agent2)


def test_remove_agent():
    """Test removing an agent."""
    manager = AgentManager()
    agent = MockAgent(name="Agent1")
    manager.add_agent(agent)
    
    manager.remove_agent("Agent1")
    assert "Agent1" not in manager.agents


def test_list_agents():
    """Test listing agents."""
    manager = AgentManager()
    manager.add_agent(MockAgent(name="Agent1"))
    manager.add_agent(MockAgent(name="Agent2"))
    
    agents = manager.list_agents()
    assert len(agents) == 2
    assert "Agent1" in agents
    assert "Agent2" in agents


def test_execute_task():
    """Test executing a task."""
    manager = AgentManager()
    manager.add_agent(MockAgent(name="Agent1"))
    
    result = manager.execute_task("Agent1", "test task")
    assert "Agent1 processed: test task" in result


def test_execute_task_nonexistent_agent():
    """Test executing task with non-existent agent."""
    manager = AgentManager()
    with pytest.raises(ValueError):
        manager.execute_task("NonExistent", "task")


def test_reset_all():
    """Test resetting all agents."""
    manager = AgentManager()
    agent1 = MockAgent(name="Agent1")
    agent2 = MockAgent(name="Agent2")
    
    manager.add_agent(agent1)
    manager.add_agent(agent2)
    
    agent1.add_message("user", "test")
    agent2.add_message("user", "test")
    
    manager.reset_all()
    
    assert len(agent1.conversation_history) == 0
    assert len(agent2.conversation_history) == 0
