# 🤖 Agentic AI Framework - Autonoma

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](./tests)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**A modular Python framework for building LLM agents with tool calling, memory, and multi-agent coordination.**

[Features](#-features) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Examples](#-examples) •
[Contributing](#-contributing)

</div>

---

## 🌟 Features

- **Modular Agent Architecture**: Easily create and customize AI agents
- **Tool/Function Calling**: Agents can use external tools and APIs
- **Memory Management**: Short-term and long-term memory systems
- **Multi-Agent Collaboration**: Agents can work together on complex tasks
- **Extensible Design**: Add new tools and capabilities easily

## 📁 Project Structure

```
Autonoma/
├── agents/     # Research, code assistant, and data analyst agents
├── core/       # BaseAgent, AgentManager, tool registry
├── memory/     # Short-term and long-term memory
├── config/     # Environment-based settings
├── examples/   # Runnable demos
├── tests/      # pytest suite
└── utils/      # Logging and helpers
```

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from agents.research_agent import ResearchAgent
from core.agent_manager import AgentManager

# Initialize agent manager
manager = AgentManager()

# Create a research agent
agent = ResearchAgent(name="Researcher")
manager.add_agent(agent)

# Run a task
result = agent.execute("Research the latest developments in AI agents")
print(result)
```

## 🤖 Available Agents

- **ResearchAgent**: Conducts research and gathers information
- **CodeAssistantAgent**: Helps with code generation and debugging
- **DataAnalystAgent**: Analyzes data and generates insights

Use `AgentManager.orchestrate()` to coordinate multiple agents with dependencies between steps.

## 🛠️ Creating Custom Agents

```python
from core.base_agent import BaseAgent
from core.tool_registry import tool

class WeatherAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(name="WeatherAgent", **kwargs)

    @tool(description="Get the current temperature for a city")
    def get_temperature(self, city: str, unit: str = "celsius") -> dict:
        """Look up the temperature.

        Args:
            city: City name
            unit: celsius or fahrenheit
        """
        return {"city": city, "temperature": 21, "unit": unit}

print(WeatherAgent().execute("Is it warm in Lisbon right now?"))
```

The model sees each `@tool` as a native function definition. The JSON schema is
built from the type hints, defaults, and the `Args:` section of the docstring.
Pass `expose_to_llm=False` to keep a tool for offline workflows only. Override
`process_offline()` to give an agent a scripted fallback when no API key is set.

## 📝 Environment Setup

Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
# Optional: any OpenAI model, or a "claude-*" model for Anthropic
DEFAULT_MODEL=
```

With a key set, agents run a tool-calling loop against the model. With an empty
`DEFAULT_MODEL`, they use `gpt-5.4-mini` (OpenAI) or `claude-haiku-5-5` (Anthropic).
Without any keys they fall back to scripted offline workflows. You can also choose
the mode per run:

```bash
python main.py --agent analyst --task "Mean and trend of 120, 135, 128, 150"
python main.py --agent code --task "Write a binary search in Python" --model claude-sonnet-5-5
python main.py --agent research --task "AI agents" --offline
```

## 🧪 Running Tests

```bash
pytest tests/
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Quick Start Guide](QUICKSTART.md) | Get up and running in 5 minutes |
| [Full Documentation](docs/DOCUMENTATION.md) | Comprehensive guides and API reference |
| [Project Structure](PROJECT_STRUCTURE.md) | Detailed project layout |
| [Contributing Guide](CONTRIBUTING.md) | How to contribute to the project |
| [GitHub Setup](GITHUB_SETUP.md) | Publishing to GitHub |

## 🎯 Use Cases

- **Customer Service Bots**: Automated support with memory and context
- **Research Assistants**: Information gathering and synthesis
- **Code Review Agents**: Automated code analysis and suggestions
- **Data Analysis Pipelines**: Multi-agent data processing workflows
- **Content Creation**: Research → Write → Edit agent chains

## 🛠️ Tech Stack

- **Language**: Python 3.10+
- **LLM APIs**: OpenAI, Anthropic
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, flake8, mypy
- **Architecture**: Async/await, Type hints, Modular design

## 📊 Project Stats

- 🐍 2,800+ lines of Python code
- 📝 26 Python modules
- 🧪 Comprehensive test suite
- 📚 Extensive documentation
- ✅ Production-ready

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

Ways to contribute:
- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🔧 Submit pull requests

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Show Your Support

If you find this project useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting issues
- 📢 Sharing with others
- 🤝 Contributing code

## 📬 Contact

- **Author**: Ilias Zaher ([Izaher18](https://github.com/Izaher18))
- **Issues**: [GitHub Issues](https://github.com/Izaher18/Autonoma/issues)
- **Email**: [izaher18@bu.edu](mailto:izaher18@bu.edu)

## 🙏 Acknowledgments

Built with modern Python best practices and inspired by the latest developments in AI agent systems.

---

<div align="center">

**[⬆ back to top](#-agentic-ai-framework)**

Made with ❤️ for building intelligent agent systems

</div>
