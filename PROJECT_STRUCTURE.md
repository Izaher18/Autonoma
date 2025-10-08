# Project Structure

```
aiagentic/
│
├── 📄 README.md                    # Project overview and documentation
├── 📄 QUICKSTART.md               # Quick start guide
├── 📄 LICENSE                     # MIT License
├── 📄 requirements.txt            # Python dependencies
├── 📄 pyproject.toml              # Project configuration
├── 📄 setup.sh                    # Automated setup script
├── 📄 main.py                     # CLI entry point
├── 📄 __init__.py                 # Package initialization
│
├── 📁 agents/                     # Agent implementations
│   ├── __init__.py
│   ├── research_agent.py          # Research & information gathering
│   ├── code_assistant.py          # Code generation & debugging
│   └── data_analyst.py            # Data analysis & insights
│
├── 📁 core/                       # Core framework
│   ├── __init__.py
│   ├── base_agent.py              # Base agent class
│   ├── agent_manager.py           # Multi-agent coordination
│   └── tool_registry.py           # Tool management
│
├── 📁 memory/                     # Memory systems
│   ├── __init__.py
│   └── memory_store.py            # Short/long-term memory
│
├── 📁 config/                     # Configuration
│   ├── __init__.py
│   └── settings.py                # App settings
│
├── 📁 utils/                      # Utilities
│   ├── __init__.py
│   ├── logging_utils.py           # Logging setup
│   └── helpers.py                 # Helper functions
│
├── 📁 examples/                   # Example scripts
│   ├── basic_usage.py             # Basic agent usage
│   ├── multi_agent.py             # Multi-agent collaboration
│   ├── memory_demo.py             # Memory system demo
│   └── custom_agent.py            # Custom agent example
│
├── 📁 tests/                      # Test suite
│   ├── conftest.py                # Test configuration
│   ├── test_base_agent.py         # Agent tests
│   ├── test_agent_manager.py     # Manager tests
│   └── test_memory.py             # Memory tests
│
├── 📁 docs/                       # Documentation
│   └── DOCUMENTATION.md           # Comprehensive docs
│
├── 📁 logs/                       # Log files (auto-created)
├── 📁 data/                       # Data storage (auto-created)
└── 📁 memory_data/                # Memory persistence (auto-created)
```

## File Descriptions

### Root Files
- **README.md**: Main project documentation with features and usage
- **QUICKSTART.md**: Get started quickly with step-by-step instructions
- **requirements.txt**: All Python dependencies
- **setup.sh**: Automated setup script (run first!)
- **main.py**: Command-line interface for running agents

### Agents (`agents/`)
Pre-built agent implementations:
- **ResearchAgent**: Information gathering and analysis
- **CodeAssistantAgent**: Code generation and debugging
- **DataAnalystAgent**: Data analysis and insights

### Core Framework (`core/`)
The heart of the system:
- **BaseAgent**: All agents inherit from this
- **AgentManager**: Coordinate multiple agents
- **ToolRegistry**: Manage agent capabilities

### Memory (`memory/`)
Persistent and temporary storage:
- **ShortTermMemory**: Recent interactions
- **LongTermMemory**: Persistent storage
- **HybridMemory**: Combines both systems

### Examples (`examples/`)
Learn by example:
- **basic_usage.py**: Single agent examples
- **multi_agent.py**: Agent collaboration
- **memory_demo.py**: Memory system usage
- **custom_agent.py**: Build your own agent

### Tests (`tests/`)
Comprehensive test suite:
- Unit tests for all components
- Run with: `pytest tests/`

## Getting Started

1. **Run setup script:**
   ```bash
   ./setup.sh
   ```

2. **Configure API keys:**
   Edit `.env` file with your keys

3. **Try examples:**
   ```bash
   python examples/basic_usage.py
   ```

4. **Use CLI:**
   ```bash
   python main.py --agent research --task "Your task here"
   ```

## Key Features by Location

### 🤖 Agents
- Pre-built specialized agents
- Easy to extend and customize
- Tool-based architecture

### 🧠 Memory
- Short-term and long-term storage
- Automatic persistence
- Search capabilities

### 🔧 Tools
- Decorator-based tool definition
- Automatic registration
- Type-safe parameters

### 👥 Multi-Agent
- Parallel execution
- Workflow orchestration
- Dependency management

## Development Workflow

1. **Create agent** in `agents/`
2. **Add tools** with `@tool` decorator
3. **Test** in `tests/`
4. **Document** in `docs/`
5. **Run** via `main.py` or examples
