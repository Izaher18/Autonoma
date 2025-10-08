"""Tool registry and decorator for agent tools."""

from typing import Callable, Optional
from functools import wraps


def tool(description: Optional[str] = None):
    """Decorator to mark a method as an agent tool.
    
    Args:
        description: Description of what the tool does
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper._is_tool = True
        wrapper._tool_description = description or func.__doc__ or "No description available"
        return wrapper
    
    return decorator


class ToolRegistry:
    """Registry for managing agent tools."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools = {}
    
    def register(self, name: str, func: Callable, description: Optional[str] = None):
        """Register a tool.
        
        Args:
            name: Tool name
            func: Tool function
            description: Tool description
        """
        self._tools[name] = {
            "function": func,
            "description": description or func.__doc__ or "No description available"
        }
    
    def get(self, name: str) -> Optional[Callable]:
        """Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool function or None if not found
        """
        tool_info = self._tools.get(name)
        return tool_info["function"] if tool_info else None
    
    def list_tools(self) -> dict:
        """List all registered tools.
        
        Returns:
            Dictionary of tool names and descriptions
        """
        return {name: info["description"] for name, info in self._tools.items()}
    
    def unregister(self, name: str):
        """Unregister a tool.
        
        Args:
            name: Tool name
        """
        if name in self._tools:
            del self._tools[name]
