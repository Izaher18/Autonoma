"""Research agent that can search and analyze information."""

import json
import logging
from typing import Dict, Any

from core.base_agent import BaseAgent
from core.tool_registry import tool

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Agent specialized in research and information gathering."""
    
    def __init__(self, name: str = "ResearchAgent"):
        """Initialize the research agent.
        
        Args:
            name: Name of the agent
        """
        system_prompt = """You are a research assistant specialized in gathering and analyzing information.
Your goal is to provide comprehensive, well-researched answers based on available data.

When conducting research:
1. Break down complex questions into smaller research tasks
2. Use available tools to gather information
3. Synthesize findings into a coherent response
4. Cite sources when possible
5. Acknowledge limitations in available data"""
        
        super().__init__(name=name, system_prompt=system_prompt)
    
    @tool(description="Search for information on a given topic")
    def search(self, query: str) -> str:
        """Search for information on a topic.
        
        Args:
            query: Search query
            
        Returns:
            Search results
        """
        # Simulated search - in production, integrate with real search API
        logger.info(f"Searching for: {query}")
        return f"Search results for '{query}':\n- Result 1: Information about {query}\n- Result 2: More details on {query}\n- Result 3: Recent developments in {query}"
    
    @tool(description="Analyze and summarize a piece of text")
    def analyze_text(self, text: str, focus: str = "general") -> str:
        """Analyze and summarize text.
        
        Args:
            text: Text to analyze
            focus: Analysis focus (general, sentiment, key_points)
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing text with focus: {focus}")
        
        word_count = len(text.split())
        char_count = len(text)
        
        analysis = f"""Text Analysis (Focus: {focus}):
- Word count: {word_count}
- Character count: {char_count}
- Summary: {text[:200]}...
"""
        return analysis
    
    @tool(description="Extract key facts from information")
    def extract_facts(self, information: str) -> Dict[str, Any]:
        """Extract key facts from information.
        
        Args:
            information: Information to extract facts from
            
        Returns:
            Dictionary of extracted facts
        """
        logger.info("Extracting facts from information")
        
        # Simulated fact extraction
        facts = {
            "extracted_at": "2025-10-08",
            "key_points": [
                "Point 1 extracted from text",
                "Point 2 extracted from text",
                "Point 3 extracted from text"
            ],
            "confidence": "high"
        }
        
        return facts
    
    async def process(self, user_input: str) -> str:
        """Process research request.
        
        Args:
            user_input: User's research query
            
        Returns:
            Research results
        """
        self.add_message("user", user_input)
        
        # Simple research workflow
        try:
            # Step 1: Search for information
            search_results = self.call_tool("search", {"query": user_input})
            
            # Step 2: Analyze the results
            analysis = self.call_tool("analyze_text", {
                "text": search_results,
                "focus": "key_points"
            })
            
            # Step 3: Extract facts
            facts = self.call_tool("extract_facts", {"information": search_results})
            
            # Compile final response
            response = f"""Research Results for: {user_input}

{search_results}

Analysis:
{analysis}

Key Facts:
{json.dumps(facts, indent=2)}
"""
            
            self.add_message("assistant", response)
            return response
            
        except Exception as e:
            error_msg = f"Error during research: {str(e)}"
            logger.error(error_msg)
            return error_msg
