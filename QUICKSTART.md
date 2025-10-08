# Agentic AI Project - Quick Start Guide

## Overview
This project provides a modular framework for building AI agents with reasoning capabilities, tool usage, and memory management.

## Installation

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

## Usage

### Run Examples

**Basic Usage:**
```bash
python examples/basic_usage.py
```

**Multi-Agent Collaboration:**
```bash
python examples/multi_agent.py
```

**Memory System:**
```bash
python examples/memory_demo.py
```

### Command Line Interface

**Research Agent:**
```bash
python main.py --agent research --task "Research quantum computing"
```

**Code Assistant:**
```bash
python main.py --agent code --task "Create a sorting algorithm"
```

**Data Analyst:**
```bash
python main.py --agent analyst --task "Analyze sales trends"
```

**Multi-Agent:**
```bash
python main.py --agent multi --task "Create a data visualization app"
```

## Project Structure

- `agents/` - Agent implementations
- `core/` - Core framework
- `memory/` - Memory systems
- `tools/` - Tool definitions
- `config/` - Configuration
- `examples/` - Example scripts
- `tests/` - Test suite
- `utils/` - Utility functions

## Creating Custom Agents

```python
from core.base_agent import BaseAgent
from core.tool_registry import tool

class MyAgent(BaseAgent):
    def __init__(self, name="MyAgent"):
        super().__init__(name=name)
    
    @tool(description="My custom tool")
    def my_tool(self, input: str) -> str:
        return f"Processed: {input}"
    
    async def process(self, user_input: str) -> str:
        result = self.call_tool("my_tool", {"input": user_input})
        return result
```

## Running Tests

```bash
pytest tests/
```

## Next Steps

1. Explore the example scripts
2. Create your own custom agents
3. Integrate with real APIs
4. Add more sophisticated tools
5. Implement advanced reasoning patterns

## Documentation

See individual module docstrings for detailed API documentation.
