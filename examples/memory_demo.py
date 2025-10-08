"""Example: Using memory systems."""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from memory.memory_store import HybridMemory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Demonstrate memory system usage."""
    
    print("=== Memory System Demo ===\n")
    
    # Initialize hybrid memory
    memory = HybridMemory(
        short_term_size=50,
        long_term_path="examples/demo_memory.json"
    )
    
    # Store some information
    print("1. Storing Information")
    print("-" * 50)
    
    memory.remember(
        key="user_preference",
        value={"theme": "dark", "language": "python"},
        important=True
    )
    print("Stored user preferences (important)")
    
    memory.remember(
        key="last_query",
        value="What are AI agents?",
        important=False
    )
    print("Stored last query (temporary)")
    
    memory.remember(
        key="project_context",
        value="Working on an agentic AI framework",
        important=True
    )
    print("Stored project context (important)\n")
    
    # Recall information
    print("2. Recalling Information")
    print("-" * 50)
    
    preferences = memory.recall("user_preference")
    print(f"User preferences: {preferences}")
    
    last_query = memory.recall("last_query")
    print(f"Last query: {last_query}")
    
    context = memory.recall("project_context")
    print(f"Project context: {context}\n")
    
    # Search memory
    print("3. Searching Memory")
    print("-" * 50)
    
    results = memory.search("python", limit=5)
    print(f"Search results for 'python': {len(results)} items found")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.get('key', 'N/A')}: {str(result['value'])[:50]}...")
    
    print("\n4. Recent Short-Term Memory")
    print("-" * 50)
    recent = memory.short_term.get_recent(3)
    print(f"Last {len(recent)} entries:")
    for entry in recent:
        print(f"  - {entry['key']}: {str(entry['value'])[:50]}...")
    
    print("\n=== Demo Complete ===")
    print("Note: Long-term memory persisted to examples/demo_memory.json")


if __name__ == "__main__":
    main()
