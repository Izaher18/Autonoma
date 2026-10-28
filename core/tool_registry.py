"""Tool registry and decorator for agent tools."""

import inspect
import re
import types
import typing
from typing import Any, Callable, Dict, Optional, Union
from functools import wraps


def tool(description: Optional[str] = None, expose_to_llm: bool = True):
    """Decorator to mark a method as an agent tool.

    Args:
        description: Description of what the tool does
        expose_to_llm: Whether the model may call this tool. Set False for
            placeholder tools that only make sense in offline mode.

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._is_tool = True
        wrapper._tool_description = description or func.__doc__ or "No description available"
        wrapper._expose_to_llm = expose_to_llm
        return wrapper

    return decorator


_JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean"}


def _json_schema(annotation: Any) -> Dict[str, Any]:
    """Map a Python type hint to a JSON schema fragment ({} accepts anything)."""
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)

    if origin in (Union, types.UnionType):
        non_none = [arg for arg in args if arg is not type(None)]
        return _json_schema(non_none[0]) if len(non_none) == 1 else {}
    if annotation in (list, tuple, set) or origin in (list, tuple, set):
        return {"type": "array", "items": _json_schema(args[0]) if args else {}}
    if annotation is dict or origin is dict:
        return {"type": "object"}
    if annotation in _JSON_TYPES:
        return {"type": _JSON_TYPES[annotation]}
    return {}


def _arg_descriptions(docstring: Optional[str]) -> Dict[str, str]:
    """Read parameter descriptions from a Google-style ``Args:`` docstring section."""
    descriptions: Dict[str, str] = {}
    in_args = False
    for line in (docstring or "").splitlines():
        stripped = line.strip()
        if stripped in ("Args:", "Arguments:"):
            in_args = True
            continue
        if not in_args:
            continue
        if not stripped or re.fullmatch(r"[A-Z]\w*:", stripped):
            break
        match = re.match(r"^(\w+)(?:\s*\([^)]*\))?:\s*(.+)$", stripped)
        if match:
            descriptions[match.group(1)] = match.group(2)
    return descriptions


def tool_schema(name: str, func: Callable) -> Dict[str, Any]:
    """Build a provider-neutral tool definition from a function's signature and docstring."""
    signature = inspect.signature(func)
    try:
        hints = typing.get_type_hints(func)
    except Exception:
        hints = {}
    arg_docs = _arg_descriptions(inspect.getdoc(func))

    properties: Dict[str, Any] = {}
    required = []
    for param_name, param in signature.parameters.items():
        if param_name == "self" or param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        schema = _json_schema(hints.get(param_name, Any))
        if param_name in arg_docs:
            schema["description"] = arg_docs[param_name]
        if param.default is param.empty:
            required.append(param_name)
        elif isinstance(param.default, (str, int, float, bool)):
            schema["default"] = param.default
        properties[param_name] = schema

    return {
        "name": name,
        "description": getattr(func, "_tool_description", None) or inspect.getdoc(func) or "",
        "parameters": {"type": "object", "properties": properties, "required": required},
    }


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
            "description": description or func.__doc__ or "No description available",
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
