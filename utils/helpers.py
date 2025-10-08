"""Helper utilities for the agent framework."""

import json
import hashlib
from typing import Any, Dict
from datetime import datetime


def generate_id(prefix: str = "id") -> str:
    """Generate a unique ID.
    
    Args:
        prefix: ID prefix
        
    Returns:
        Unique ID string
    """
    timestamp = datetime.now().isoformat()
    hash_str = hashlib.md5(timestamp.encode()).hexdigest()[:8]
    return f"{prefix}_{hash_str}"


def serialize_json(obj: Any) -> str:
    """Serialize object to JSON string.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON string
    """
    return json.dumps(obj, indent=2, default=str)


def deserialize_json(json_str: str) -> Any:
    """Deserialize JSON string to object.
    
    Args:
        json_str: JSON string
        
    Returns:
        Deserialized object
    """
    return json.loads(json_str)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_timestamp(dt: datetime = None) -> str:
    """Format datetime as string.
    
    Args:
        dt: Datetime object (default: now)
        
    Returns:
        Formatted timestamp
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def merge_dicts(*dicts: Dict) -> Dict:
    """Merge multiple dictionaries.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Division result or default
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default
