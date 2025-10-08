"""Memory management system for agents."""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryStore:
    """Base class for memory storage."""
    
    def add(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """Add an entry to memory."""
        raise NotImplementedError
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve an entry from memory."""
        raise NotImplementedError
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for relevant entries."""
        raise NotImplementedError
    
    def clear(self):
        """Clear all memory."""
        raise NotImplementedError


class ShortTermMemory(MemoryStore):
    """Short-term memory for recent interactions."""
    
    def __init__(self, max_size: int = 100):
        """Initialize short-term memory.
        
        Args:
            max_size: Maximum number of items to store
        """
        self.max_size = max_size
        self.memory: List[Dict[str, Any]] = []
        logger.info(f"Initialized ShortTermMemory with max_size={max_size}")
    
    def add(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """Add an entry to short-term memory.
        
        Args:
            key: Entry key
            value: Entry value
            metadata: Optional metadata
        """
        entry = {
            "key": key,
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.memory.append(entry)
        
        # Remove oldest entries if over max size
        if len(self.memory) > self.max_size:
            self.memory = self.memory[-self.max_size:]
        
        logger.debug(f"Added to short-term memory: {key}")
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve the most recent entry with the given key.
        
        Args:
            key: Entry key
            
        Returns:
            Entry value or None
        """
        for entry in reversed(self.memory):
            if entry["key"] == key:
                return entry["value"]
        return None
    
    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get the n most recent entries.
        
        Args:
            n: Number of entries to retrieve
            
        Returns:
            List of recent entries
        """
        return self.memory[-n:]
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for entries matching the query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching entries
        """
        results = []
        query_lower = query.lower()
        
        for entry in reversed(self.memory):
            value_str = str(entry["value"]).lower()
            if query_lower in value_str or query_lower in entry["key"].lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        
        return results
    
    def clear(self):
        """Clear all short-term memory."""
        self.memory = []
        logger.info("Cleared short-term memory")


class LongTermMemory(MemoryStore):
    """Long-term persistent memory."""
    
    def __init__(self, storage_path: str = "memory_store.json"):
        """Initialize long-term memory.
        
        Args:
            storage_path: Path to storage file
        """
        self.storage_path = Path(storage_path)
        self.memory: Dict[str, Dict[str, Any]] = {}
        
        # Load existing memory if available
        self._load()
        
        logger.info(f"Initialized LongTermMemory at {storage_path}")
    
    def _load(self):
        """Load memory from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    self.memory = json.load(f)
                logger.info(f"Loaded {len(self.memory)} entries from long-term memory")
            except Exception as e:
                logger.error(f"Error loading long-term memory: {e}")
    
    def _save(self):
        """Save memory to disk."""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
            logger.debug("Saved long-term memory to disk")
        except Exception as e:
            logger.error(f"Error saving long-term memory: {e}")
    
    def add(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """Add an entry to long-term memory.
        
        Args:
            key: Entry key
            value: Entry value
            metadata: Optional metadata
        """
        self.memory[key] = {
            "value": value,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "access_count": 0
        }
        
        self._save()
        logger.debug(f"Added to long-term memory: {key}")
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve an entry from long-term memory.
        
        Args:
            key: Entry key
            
        Returns:
            Entry value or None
        """
        if key in self.memory:
            entry = self.memory[key]
            entry["access_count"] += 1
            entry["last_accessed"] = datetime.now().isoformat()
            self._save()
            return entry["value"]
        return None
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search long-term memory.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching entries
        """
        results = []
        query_lower = query.lower()
        
        for key, entry in self.memory.items():
            value_str = str(entry["value"]).lower()
            if query_lower in value_str or query_lower in key.lower():
                results.append({
                    "key": key,
                    "value": entry["value"],
                    "metadata": entry["metadata"],
                    "timestamp": entry["timestamp"]
                })
                if len(results) >= limit:
                    break
        
        return results
    
    def clear(self):
        """Clear all long-term memory."""
        self.memory = {}
        self._save()
        logger.info("Cleared long-term memory")


class HybridMemory:
    """Hybrid memory system combining short-term and long-term memory."""
    
    def __init__(
        self,
        short_term_size: int = 100,
        long_term_path: str = "memory_store.json"
    ):
        """Initialize hybrid memory system.
        
        Args:
            short_term_size: Size of short-term memory
            long_term_path: Path to long-term storage
        """
        self.short_term = ShortTermMemory(max_size=short_term_size)
        self.long_term = LongTermMemory(storage_path=long_term_path)
        
        logger.info("Initialized HybridMemory system")
    
    def remember(self, key: str, value: Any, important: bool = False, metadata: Optional[Dict] = None):
        """Store information in memory.
        
        Args:
            key: Entry key
            value: Entry value
            important: If True, store in long-term memory
            metadata: Optional metadata
        """
        # Always add to short-term memory
        self.short_term.add(key, value, metadata)
        
        # Add to long-term if important
        if important:
            self.long_term.add(key, value, metadata)
    
    def recall(self, key: str) -> Optional[Any]:
        """Retrieve information from memory.
        
        Args:
            key: Entry key
            
        Returns:
            Entry value or None
        """
        # Check short-term first
        value = self.short_term.get(key)
        if value is not None:
            return value
        
        # Check long-term
        return self.long_term.get(key)
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search both memory systems.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Combined search results
        """
        short_results = self.short_term.search(query, limit)
        long_results = self.long_term.search(query, limit)
        
        # Combine and deduplicate
        all_results = short_results + long_results
        seen_keys = set()
        unique_results = []
        
        for result in all_results:
            key = result.get("key", str(result["value"]))
            if key not in seen_keys:
                seen_keys.add(key)
                unique_results.append(result)
                if len(unique_results) >= limit:
                    break
        
        return unique_results
    
    def clear_all(self):
        """Clear both memory systems."""
        self.short_term.clear()
        self.long_term.clear()
        logger.info("Cleared all memory systems")
