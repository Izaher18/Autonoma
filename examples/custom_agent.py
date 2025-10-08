"""Example: Custom agent with advanced features."""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.base_agent import BaseAgent
from core.tool_registry import tool
from memory.memory_store import HybridMemory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class CustomAgent(BaseAgent):
    """Custom agent with memory and advanced reasoning."""
    
    def __init__(self, name="CustomAgent"):
        """Initialize custom agent."""
        system_prompt = """You are an advanced AI assistant with memory capabilities.
        
You can:
1. Remember information across conversations
2. Perform complex reasoning
3. Use multiple tools in sequence
4. Learn from past interactions

Always think step by step and use available tools effectively."""
        
        super().__init__(name=name, system_prompt=system_prompt)
        
        # Initialize memory
        self.memory = HybridMemory(
            short_term_size=100,
            long_term_path="data/custom_agent_memory.json"
        )
        
        # Initialize custom state
        self.state["interaction_count"] = 0
        self.state["topics_discussed"] = []
    
    @tool(description="Store information in long-term memory")
    def remember(self, key: str, value: str, important: bool = True) -> str:
        """Store information in memory.
        
        Args:
            key: Memory key
            value: Value to store
            important: Whether to store in long-term memory
            
        Returns:
            Confirmation message
        """
        self.memory.remember(key, value, important=important)
        logger.info(f"Stored in memory: {key}")
        return f"Remembered: {key} = {value}"
    
    @tool(description="Recall information from memory")
    def recall(self, key: str) -> str:
        """Recall information from memory.
        
        Args:
            key: Memory key
            
        Returns:
            Recalled value or error message
        """
        value = self.memory.recall(key)
        if value:
            logger.info(f"Recalled from memory: {key}")
            return f"Recalled: {key} = {value}"
        return f"No memory found for key: {key}"
    
    @tool(description="Search memory for relevant information")
    def search_memory(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Search memory for relevant information.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Search results
        """
        results = self.memory.search(query, limit=limit)
        logger.info(f"Memory search for '{query}' returned {len(results)} results")
        
        return {
            "query": query,
            "results_count": len(results),
            "results": results
        }
    
    @tool(description="Analyze text and extract key information")
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text and extract key information.
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results
        """
        words = text.split()
        sentences = text.split('.')
        
        analysis = {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "unique_words": len(set(words)),
            "summary": text[:200] + "..." if len(text) > 200 else text
        }
        
        logger.info(f"Analyzed text: {analysis['word_count']} words")
        return analysis
    
    @tool(description="Generate a summary of conversation history")
    def summarize_conversation(self) -> str:
        """Generate a summary of the conversation.
        
        Returns:
            Conversation summary
        """
        summary = f"""Conversation Summary:
- Total interactions: {self.state['interaction_count']}
- Topics discussed: {', '.join(self.state['topics_discussed']) if self.state['topics_discussed'] else 'None'}
- Messages exchanged: {len(self.conversation_history)}
- Memory items stored: {len(self.memory.short_term.memory)}
"""
        return summary
    
    async def process(self, user_input: str) -> str:
        """Process user input with advanced reasoning.
        
        Args:
            user_input: User's input
            
        Returns:
            Agent's response
        """
        # Update state
        self.state["interaction_count"] += 1
        self.add_message("user", user_input)
        
        logger.info(f"Processing interaction #{self.state['interaction_count']}")
        
        try:
            # Determine action based on input
            response_parts = []
            
            # Check if user wants to remember something
            if "remember" in user_input.lower():
                result = self.call_tool("remember", {
                    "key": f"note_{self.state['interaction_count']}",
                    "value": user_input,
                    "important": True
                })
                response_parts.append(result)
            
            # Check if user wants to recall something
            elif "recall" in user_input.lower() or "what did" in user_input.lower():
                memory_results = self.call_tool("search_memory", {
                    "query": user_input,
                    "limit": 3
                })
                response_parts.append(f"Found {memory_results['results_count']} relevant memories")
            
            # Analyze the input
            analysis = self.call_tool("analyze", {"text": user_input})
            response_parts.append(f"Input analysis: {analysis['word_count']} words")
            
            # Check if user wants a summary
            if "summary" in user_input.lower():
                summary = self.call_tool("summarize_conversation", {})
                response_parts.append(summary)
            
            # Generate final response
            if not response_parts:
                response_parts.append("I've processed your input and can help with various tasks.")
            
            response = "\n\n".join(response_parts)
            
            # Store interaction in memory
            self.memory.remember(
                f"interaction_{self.state['interaction_count']}",
                {
                    "input": user_input,
                    "response": response,
                    "timestamp": str(self.conversation_history[-1].timestamp)
                },
                important=False
            )
            
            self.add_message("assistant", response)
            return response
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg


def main():
    """Demonstrate custom agent usage."""
    
    print("=== Custom Agent Demo ===\n")
    
    agent = CustomAgent()
    
    # Test interactions
    test_inputs = [
        "Remember that I like Python programming",
        "What are the benefits of AI agents?",
        "Can you recall what I told you earlier?",
        "Please give me a summary of our conversation"
    ]
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n{'='*60}")
        print(f"Interaction {i}")
        print(f"{'='*60}")
        print(f"User: {input_text}")
        print(f"\nAgent:")
        
        result = agent.execute(input_text)
        print(result)
    
    print(f"\n{'='*60}")
    print("Demo Complete")
    print(f"{'='*60}")
    
    # Show agent state
    print(f"\nAgent State:")
    print(f"- Interactions: {agent.state['interaction_count']}")
    print(f"- Messages: {len(agent.conversation_history)}")
    print(f"- Memory items: {len(agent.memory.short_term.memory)}")


if __name__ == "__main__":
    main()
