"""Agent manager for coordinating multiple agents."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentManager:
    """Manages multiple agents and coordinates their interactions."""
    
    def __init__(self, max_workers: int = 5):
        """Initialize the agent manager.
        
        Args:
            max_workers: Maximum number of concurrent agent executions
        """
        self.agents: Dict[str, BaseAgent] = {}
        self.max_workers = max_workers
        self.execution_history: List[Dict[str, Any]] = []
        
        logger.info("Initialized AgentManager")
    
    def add_agent(self, agent: BaseAgent):
        """Add an agent to the manager.
        
        Args:
            agent: Agent instance to add
            
        Raises:
            ValueError: If agent with same name already exists
        """
        if agent.config.name in self.agents:
            raise ValueError(f"Agent with name '{agent.config.name}' already exists")
        
        self.agents[agent.config.name] = agent
        logger.info(f"Added agent: {agent.config.name}")
    
    def remove_agent(self, name: str):
        """Remove an agent from the manager.
        
        Args:
            name: Name of the agent to remove
        """
        if name in self.agents:
            del self.agents[name]
            logger.info(f"Removed agent: {name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(self.agents.keys())
    
    def execute_task(self, agent_name: str, task: str) -> str:
        """Execute a task with a specific agent.
        
        Args:
            agent_name: Name of the agent to use
            task: Task description
            
        Returns:
            Task result
            
        Raises:
            ValueError: If agent not found
        """
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found")
        
        logger.info(f"Executing task with agent {agent_name}: {task[:100]}")
        
        result = agent.execute(task)
        
        # Record execution
        self.execution_history.append({
            "agent": agent_name,
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        
        return result
    
    def execute_parallel(self, tasks: List[Dict[str, str]]) -> List[str]:
        """Execute multiple tasks in parallel.
        
        Args:
            tasks: List of dicts with 'agent' and 'task' keys
            
        Returns:
            List of results in the same order as tasks
        """
        results = [None] * len(tasks)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self.execute_task, task["agent"], task["task"]): i
                for i, task in enumerate(tasks)
            }
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    logger.error(f"Task {index} failed: {str(e)}")
                    results[index] = f"Error: {str(e)}"
        
        return results
    
    def orchestrate(self, plan: List[Dict[str, str]]) -> Dict[str, Any]:
        """Orchestrate a complex workflow with multiple agents.
        
        Args:
            plan: List of steps, each with 'agent', 'task', and optional 'depends_on'
            
        Returns:
            Dictionary with final results and execution trace
        """
        results = {}
        execution_order = []
        
        # Simple dependency resolution (assumes no circular dependencies)
        remaining = plan.copy()
        
        while remaining:
            # Find tasks with satisfied dependencies
            ready = []
            for task in remaining:
                depends_on = task.get("depends_on", [])
                if all(dep in results for dep in depends_on):
                    ready.append(task)
            
            if not ready:
                raise ValueError("Circular dependency or missing dependency detected")
            
            # Execute ready tasks
            for task in ready:
                task_id = task.get("id", f"task_{len(execution_order)}")
                
                # Substitute results from dependencies
                task_text = task["task"]
                for dep_id in task.get("depends_on", []):
                    task_text = task_text.replace(f"{{{{dep_id}}}}", str(results[dep_id]))
                
                result = self.execute_task(task["agent"], task_text)
                results[task_id] = result
                execution_order.append(task_id)
                remaining.remove(task)
        
        return {
            "results": results,
            "execution_order": execution_order
        }
    
    def reset_all(self):
        """Reset all agents in the manager."""
        for agent in self.agents.values():
            agent.reset()
        self.execution_history = []
        logger.info("Reset all agents")
