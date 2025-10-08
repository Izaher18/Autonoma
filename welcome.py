#!/usr/bin/env python3
"""
Interactive welcome script for the Agentic AI project.
Run this to get an overview and quick start guide.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))


def print_banner():
    """Print welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              🤖  AGENTIC AI FRAMEWORK  🤖                        ║
║                                                                  ║
║        A Modular Framework for Building AI Agents                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_features():
    """Print key features."""
    features = """
✨ KEY FEATURES:
   
   🎯 Modular Agent Architecture
      → Easy to create and customize AI agents
      → Pre-built agents for common tasks
   
   🛠️  Tool/Function Calling
      → Agents can use external tools and APIs
      → Simple decorator-based tool definition
   
   🧠 Memory Management
      → Short-term and long-term memory systems
      → Persistent storage across sessions
   
   👥 Multi-Agent Collaboration
      → Coordinate multiple agents
      → Parallel and sequential execution
   
   🔌 Extensible Design
      → Add new tools and capabilities easily
      → Plugin-friendly architecture
"""
    print(features)


def print_quick_start():
    """Print quick start guide."""
    quick_start = """
🚀 QUICK START:

   1. Setup (First Time):
      $ ./setup.sh
   
   2. Configure API Keys:
      $ cp .env.example .env
      $ nano .env  # Add your API keys
   
   3. Run Examples:
      $ python examples/basic_usage.py
      $ python examples/multi_agent.py
      $ python examples/memory_demo.py
   
   4. Use CLI:
      $ python main.py --agent research --task "Research AI agents"
      $ python main.py --agent code --task "Create sorting function"
      $ python main.py --agent analyst --task "Analyze data trends"
"""
    print(quick_start)


def print_available_agents():
    """Print available agents."""
    agents = """
🤖 AVAILABLE AGENTS:

   📚 Research Agent
      → Conducts research and gathers information
      → Analyzes and synthesizes findings
   
   💻 Code Assistant Agent
      → Generates code in multiple languages
      → Debugs and optimizes existing code
   
   📊 Data Analyst Agent
      → Analyzes data and identifies trends
      → Generates insights and visualizations
   
   🎭 Custom Agents
      → Create your own specialized agents
      → See examples/custom_agent.py
"""
    print(agents)


def print_project_structure():
    """Print project structure."""
    structure = """
📁 PROJECT STRUCTURE:

   aiagentic/
   ├── 📄 Setup & Config
   │   ├── setup.sh          (Run this first!)
   │   ├── requirements.txt  (Dependencies)
   │   └── .env.example      (Configuration template)
   │
   ├── 🤖 Agents
   │   └── agents/           (Pre-built and custom agents)
   │
   ├── 🧠 Core
   │   ├── core/             (Framework components)
   │   ├── memory/           (Memory systems)
   │   └── utils/            (Helper utilities)
   │
   ├── 📚 Learning
   │   ├── examples/         (Example scripts)
   │   ├── tests/            (Test suite)
   │   └── docs/             (Documentation)
   │
   └── 🔧 Tools
       └── main.py           (CLI interface)
"""
    print(structure)


def print_resources():
    """Print helpful resources."""
    resources = """
📚 RESOURCES:

   📖 Documentation:
      → README.md              (Overview)
      → QUICKSTART.md          (Quick start guide)
      → PROJECT_STRUCTURE.md   (Project layout)
      → docs/DOCUMENTATION.md  (Comprehensive docs)
   
   🎓 Examples:
      → examples/basic_usage.py    (Single agent usage)
      → examples/multi_agent.py    (Multi-agent collaboration)
      → examples/memory_demo.py    (Memory system)
      → examples/custom_agent.py   (Build your own)
   
   🧪 Testing:
      → pytest tests/              (Run all tests)
      → pytest tests/test_*.py     (Run specific tests)
"""
    print(resources)


def print_next_steps():
    """Print next steps."""
    next_steps = """
🎯 NEXT STEPS:

   1. ✅ Run setup script:        ./setup.sh
   2. ✅ Add API keys:            Edit .env file
   3. ✅ Try examples:            python examples/basic_usage.py
   4. ✅ Read documentation:      cat docs/DOCUMENTATION.md
   5. ✅ Create custom agent:     Follow examples/custom_agent.py
   6. ✅ Run tests:               pytest tests/
   7. ✅ Build something cool:    Use the framework!

"""
    print(next_steps)


def print_footer():
    """Print footer."""
    footer = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  Need help? Check the documentation or run examples!            ║
║                                                                  ║
║  Happy building! 🚀                                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

"""
    print(footer)


def main():
    """Main function."""
    print_banner()
    print_features()
    print_available_agents()
    print_quick_start()
    print_project_structure()
    print_resources()
    print_next_steps()
    print_footer()
    
    # Check if setup has been run
    if not Path("venv").exists():
        print("⚠️  Virtual environment not found!")
        print("   Run './setup.sh' to set up the project.\n")
    elif not Path(".env").exists():
        print("⚠️  .env file not found!")
        print("   Copy .env.example to .env and add your API keys.\n")
    else:
        print("✅ Project appears to be set up!\n")
        print("   Try: python examples/basic_usage.py\n")


if __name__ == "__main__":
    main()
