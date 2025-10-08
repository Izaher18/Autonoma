"""Example: Multi-agent collaboration."""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.agent_manager import AgentManager
from agents.research_agent import ResearchAgent
from agents.code_assistant import CodeAssistantAgent
from agents.data_analyst import DataAnalystAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Demonstrate multi-agent collaboration."""
    
    print("=== Multi-Agent Collaboration Demo ===\n")
    
    # Create agent manager
    manager = AgentManager(max_workers=3)
    
    # Add agents
    manager.add_agent(ResearchAgent(name="Researcher"))
    manager.add_agent(CodeAssistantAgent(name="Coder"))
    manager.add_agent(DataAnalystAgent(name="Analyst"))
    
    print(f"Active agents: {manager.list_agents()}\n")
    
    # Example 1: Sequential execution
    print("Example 1: Sequential Task Execution")
    print("-" * 50)
    
    tasks = [
        {"agent": "Researcher", "task": "Research machine learning algorithms"},
        {"agent": "Coder", "task": "Generate a simple ML model"},
        {"agent": "Analyst", "task": "Analyze model performance"}
    ]
    
    for task in tasks:
        print(f"\nAgent: {task['agent']}")
        print(f"Task: {task['task']}")
        result = manager.execute_task(task["agent"], task["task"])
        print(f"Result preview: {result[:200]}...")
    
    # Example 2: Parallel execution
    print("\n\nExample 2: Parallel Task Execution")
    print("-" * 50)
    
    parallel_tasks = [
        {"agent": "Researcher", "task": "Research Python best practices"},
        {"agent": "Coder", "task": "Create a utility function"},
        {"agent": "Analyst", "task": "Analyze code metrics"}
    ]
    
    print("Executing tasks in parallel...")
    results = manager.execute_parallel(parallel_tasks)
    
    for i, result in enumerate(results):
        print(f"\nTask {i+1} result preview: {result[:200]}...")
    
    # Example 3: Orchestrated workflow
    print("\n\nExample 3: Orchestrated Workflow")
    print("-" * 50)
    
    workflow = [
        {
            "id": "research",
            "agent": "Researcher",
            "task": "Research data visualization libraries"
        },
        {
            "id": "code",
            "agent": "Coder",
            "task": "Generate code for data visualization using research findings",
            "depends_on": ["research"]
        },
        {
            "id": "analysis",
            "agent": "Analyst",
            "task": "Analyze the visualization code quality",
            "depends_on": ["code"]
        }
    ]
    
    print("Executing orchestrated workflow...")
    orchestration_result = manager.orchestrate(workflow)
    
    print(f"\nExecution order: {orchestration_result['execution_order']}")
    print(f"Number of completed tasks: {len(orchestration_result['results'])}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
