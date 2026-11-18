# 🤖 Agentic AI Framework - Autonoma

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](./tests)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**A personal AI agent that gets work done — not just a chatbot you prompt.**

Talk to Autonoma like a chief of staff. It remembers what matters, calls specialists when needed, and shows you what it's doing.

[Features](#-features) •
[Web UI](#-web-ui) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Contributing](#-contributing)

</div>

---

## 🌟 Features

- **Personal assistant first**: Autonoma understands goals in everyday language
- **Specialist team**: Research, code, and data agents work behind the scenes
- **Memory**: Short-term and long-term recall across a conversation
- **Tool calling**: Native OpenAI / Anthropic function calling
- **Web UI**: Muse-style chat interface with live activity trail
- **Offline demos**: Scripted workflows when no API key is set

## 💬 Web UI

```bash
pip install -r requirements.txt
python main.py --web
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Pick Autonoma (or a specialist), talk naturally, and watch tools/specialists fire in the activity trail.

## 📁 Project Structure

```
Autonoma/
├── agents/     # Autonoma + research, code, analyst specialists
├── core/       # BaseAgent, LLM clients, tool registry
├── memory/     # Short-term and long-term memory
├── web/        # FastAPI chat UI
├── config/     # Environment-based settings
├── examples/   # Runnable demos
├── tests/      # pytest suite
└── utils/      # Logging and helpers
```

## 🚀 Quick Start

### Installation

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # add your API keys
```

### Talk to Autonoma (CLI)

```bash
python main.py --agent autonoma --task "Remember I prefer Python, then draft a retry helper"
python main.py --web
```

### Basic Usage

```python
from agents import AutonomaAgent

assistant = AutonomaAgent()
print(assistant.execute("Brief me on personal AI agents, then note that I care about privacy"))
```

## 🤖 Available Agents

- **AutonomaAgent**: Personal assistant — remembers context, delegates to specialists
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
