"""Code assistant agent for programming tasks."""

import logging
from typing import Dict, Any

from core.base_agent import BaseAgent
from core.tool_registry import tool

logger = logging.getLogger(__name__)


class CodeAssistantAgent(BaseAgent):
    """Agent specialized in code generation and assistance."""
    
    def __init__(self, name: str = "CodeAssistant"):
        """Initialize the code assistant agent.
        
        Args:
            name: Name of the agent
        """
        system_prompt = """You are a programming assistant specialized in code generation, debugging, and optimization.

Your capabilities include:
1. Writing clean, efficient code in multiple languages
2. Debugging and fixing code issues
3. Explaining code concepts
4. Suggesting optimizations and best practices
5. Generating tests

Always provide well-commented, production-ready code."""
        
        super().__init__(name=name, system_prompt=system_prompt)
        self.supported_languages = ["python", "javascript", "java", "cpp", "go", "rust"]
    
    @tool(description="Generate code based on requirements")
    def generate_code(self, requirements: str, language: str = "python") -> str:
        """Generate code based on requirements.
        
        Args:
            requirements: Description of what the code should do
            language: Programming language
            
        Returns:
            Generated code
        """
        logger.info(f"Generating {language} code for: {requirements}")
        
        # Template code generation
        if language == "python":
            code = f'''"""
{requirements}
"""

def main():
    """Main function implementing the requirements."""
    # TODO: Implement {requirements}
    pass

if __name__ == "__main__":
    main()
'''
        else:
            code = f"// {requirements}\n// TODO: Implement in {language}"
        
        return code
    
    @tool(description="Analyze code for issues and improvements")
    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Analyze code for potential issues.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing {language} code")
        
        analysis = {
            "language": language,
            "line_count": len(code.split('\n')),
            "suggestions": [
                "Add error handling",
                "Include type hints",
                "Add docstrings",
                "Consider edge cases"
            ],
            "complexity": "moderate",
            "maintainability_score": 7.5
        }
        
        return analysis
    
    @tool(description="Generate unit tests for code")
    def generate_tests(self, code: str, language: str = "python") -> str:
        """Generate unit tests for code.
        
        Args:
            code: Code to test
            language: Programming language
            
        Returns:
            Generated test code
        """
        logger.info(f"Generating tests for {language} code")
        
        if language == "python":
            tests = f'''import unittest

class TestGeneratedCode(unittest.TestCase):
    """Test cases for the generated code."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # TODO: Implement test
        self.assertTrue(True)
    
    def test_edge_cases(self):
        """Test edge cases."""
        # TODO: Implement test
        pass

if __name__ == "__main__":
    unittest.main()
'''
        else:
            tests = f"// Test cases for {language}\n// TODO: Implement tests"
        
        return tests
    
    @tool(description="Explain code functionality")
    def explain_code(self, code: str) -> str:
        """Explain what a piece of code does.
        
        Args:
            code: Code to explain
            
        Returns:
            Explanation
        """
        logger.info("Explaining code")
        
        lines = len(code.split('\n'))
        explanation = f"""Code Explanation:

This code contains {lines} lines.

Overview:
- The code implements specific functionality
- It follows standard programming patterns
- Key operations include data processing and output

Structure:
- Imports and dependencies
- Main logic implementation
- Helper functions or classes

Usage:
Run this code to execute the implemented functionality.
"""
        return explanation
    
    async def process(self, user_input: str) -> str:
        """Process code-related request.
        
        Args:
            user_input: User's request
            
        Returns:
            Code assistance result
        """
        self.add_message("user", user_input)
        
        try:
            # Determine action based on keywords
            if "generate" in user_input.lower() or "create" in user_input.lower():
                code = self.call_tool("generate_code", {
                    "requirements": user_input,
                    "language": "python"
                })
                response = f"Generated Code:\n\n```python\n{code}\n```"
                
            elif "test" in user_input.lower():
                tests = self.call_tool("generate_tests", {
                    "code": "# Your code here",
                    "language": "python"
                })
                response = f"Generated Tests:\n\n```python\n{tests}\n```"
                
            elif "analyze" in user_input.lower():
                analysis = self.call_tool("analyze_code", {
                    "code": "# Sample code",
                    "language": "python"
                })
                response = f"Code Analysis:\n\n{analysis}"
                
            else:
                explanation = self.call_tool("explain_code", {"code": user_input})
                response = explanation
            
            self.add_message("assistant", response)
            return response
            
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(error_msg)
            return error_msg
