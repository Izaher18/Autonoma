"""Tests for memory systems."""

import pytest
import tempfile
from pathlib import Path
from memory.memory_store import ShortTermMemory, LongTermMemory, HybridMemory


def test_short_term_memory_add():
    """Test adding to short-term memory."""
    memory = ShortTermMemory(max_size=5)
    memory.add("key1", "value1")
    
    assert memory.get("key1") == "value1"


def test_short_term_memory_max_size():
    """Test short-term memory respects max size."""
    memory = ShortTermMemory(max_size=3)
    
    for i in range(5):
        memory.add(f"key{i}", f"value{i}")
    
    assert len(memory.memory) == 3
    assert memory.get("key0") is None  # Oldest should be removed
    assert memory.get("key4") == "value4"


def test_short_term_memory_get_recent():
    """Test getting recent entries."""
    memory = ShortTermMemory()
    
    for i in range(5):
        memory.add(f"key{i}", f"value{i}")
    
    recent = memory.get_recent(3)
    assert len(recent) == 3
    assert recent[-1]["key"] == "key4"


def test_short_term_memory_search():
    """Test searching short-term memory."""
    memory = ShortTermMemory()
    memory.add("user_name", "Alice")
    memory.add("user_age", 30)
    memory.add("project_name", "AI Agent")
    
    results = memory.search("user", limit=5)
    assert len(results) >= 2


def test_short_term_memory_clear():
    """Test clearing short-term memory."""
    memory = ShortTermMemory()
    memory.add("key1", "value1")
    memory.clear()
    
    assert len(memory.memory) == 0


def test_long_term_memory_persistence():
    """Test long-term memory persistence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_memory.json"
        
        # Create and add data
        memory1 = LongTermMemory(storage_path=str(storage_path))
        memory1.add("key1", "value1")
        
        # Create new instance and check data persisted
        memory2 = LongTermMemory(storage_path=str(storage_path))
        assert memory2.get("key1") == "value1"


def test_long_term_memory_access_count():
    """Test long-term memory tracks access count."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_memory.json"
        memory = LongTermMemory(storage_path=str(storage_path))
        
        memory.add("key1", "value1")
        
        # Access multiple times
        memory.get("key1")
        memory.get("key1")
        
        assert memory.memory["key1"]["access_count"] == 2


def test_hybrid_memory_remember():
    """Test hybrid memory remember method."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_memory.json"
        memory = HybridMemory(
            short_term_size=10,
            long_term_path=str(storage_path)
        )
        
        # Add non-important (short-term only)
        memory.remember("temp_key", "temp_value", important=False)
        assert memory.short_term.get("temp_key") == "temp_value"
        assert memory.long_term.get("temp_key") is None
        
        # Add important (both)
        memory.remember("important_key", "important_value", important=True)
        assert memory.short_term.get("important_key") == "important_value"
        assert memory.long_term.get("important_key") == "important_value"


def test_hybrid_memory_recall():
    """Test hybrid memory recall method."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_memory.json"
        memory = HybridMemory(long_term_path=str(storage_path))
        
        memory.remember("key1", "value1", important=True)
        
        result = memory.recall("key1")
        assert result == "value1"


def test_hybrid_memory_search():
    """Test hybrid memory search."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_memory.json"
        memory = HybridMemory(long_term_path=str(storage_path))
        
        memory.remember("python_fact", "Python is awesome", important=True)
        memory.remember("python_version", "3.10", important=False)
        
        results = memory.search("python", limit=5)
        assert len(results) >= 2
