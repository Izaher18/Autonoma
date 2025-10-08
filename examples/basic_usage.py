"""Example: Basic agent usage."""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.research_agent import ResearchAgent
from agents.code_assistant import CodeAssistantAgent
from agents.data_analyst import DataAnalystAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Demonstrate basic agent usage."""
    
    print("=== Agentic AI Framework Demo ===\n")
    
    # 1. Research Agent Example
    print("1. Research Agent")
    print("-" * 50)
    research_agent = ResearchAgent()
    result = research_agent.execute("Research the benefits of AI agents")
    print(result)
    print("\n")
    
    # 2. Code Assistant Example
    print("2. Code Assistant Agent")
    print("-" * 50)
    code_agent = CodeAssistantAgent()
    result = code_agent.execute("Generate a function to calculate fibonacci numbers")
    print(result)
    print("\n")
    
    # 3. Data Analyst Example
    print("3. Data Analyst Agent")
    print("-" * 50)
    analyst_agent = DataAnalystAgent()
    result = analyst_agent.execute("Analyze sales data trends")
    print(result)
    print("\n")
    
    print("=== Demo Complete ===")


if __name__ == "__main__":
    main()
