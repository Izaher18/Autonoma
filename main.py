"""Main entry point for running agents or the web UI."""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from utils.logging_utils import setup_logging
from config.settings import Config
from agents import AutonomaAgent, ResearchAgent, CodeAssistantAgent, DataAnalystAgent
from core.agent_manager import AgentManager

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Autonoma — personal AI agent framework")
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch the Autonoma chat UI at http://127.0.0.1:8000",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for --web (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for --web (default: 8000)",
    )
    parser.add_argument(
        "--agent",
        choices=["autonoma", "research", "code", "analyst", "multi"],
        default="autonoma",
        help="Agent type to run",
    )
    parser.add_argument("--task", type=str, help="Task description for the agent")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--model", type=str, default=None, help="Model to use (overrides DEFAULT_MODEL)"
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run the scripted offline workflows instead of calling an LLM",
    )

    args = parser.parse_args()

    setup_logging(level="DEBUG" if args.verbose else None)

    if args.web:
        import uvicorn

        logger.info(f"Starting Autonoma UI on http://{args.host}:{args.port}")
        uvicorn.run("web.app:app", host=args.host, port=args.port, reload=False)
        return

    if not args.task:
        parser.error("--task is required unless you pass --web")

    if args.offline:
        logger.info("Offline mode: using scripted workflows, no LLM calls")
    elif not Config.validate():
        logger.warning("No API keys set; running scripted offline workflows instead of an LLM")

    agent_options = {"model": args.model, "use_llm": not args.offline}
    logger.info(f"Starting {args.agent} agent with task: {args.task}")

    try:
        if args.agent == "autonoma":
            agent = AutonomaAgent(**agent_options)
            result = agent.execute(args.task)
            print("\n" + "=" * 60)
            print("AUTONOMA:")
            print("=" * 60)
            print(result)

        elif args.agent == "research":
            agent = ResearchAgent(**agent_options)
            result = agent.execute(args.task)
            print("\n" + "=" * 60)
            print("RESEARCH RESULTS:")
            print("=" * 60)
            print(result)

        elif args.agent == "code":
            agent = CodeAssistantAgent(**agent_options)
            result = agent.execute(args.task)
            print("\n" + "=" * 60)
            print("CODE ASSISTANT RESULTS:")
            print("=" * 60)
            print(result)

        elif args.agent == "analyst":
            agent = DataAnalystAgent(**agent_options)
            result = agent.execute(args.task)
            print("\n" + "=" * 60)
            print("DATA ANALYSIS RESULTS:")
            print("=" * 60)
            print(result)

        elif args.agent == "multi":
            manager = AgentManager()
            manager.add_agent(ResearchAgent(name="Researcher", **agent_options))
            manager.add_agent(CodeAssistantAgent(name="Coder", **agent_options))
            manager.add_agent(DataAnalystAgent(name="Analyst", **agent_options))

            print("\n" + "=" * 60)
            print("MULTI-AGENT EXECUTION:")
            print("=" * 60)

            for agent_name in manager.list_agents():
                print(f"\n--- {agent_name} ---")
                result = manager.execute_task(agent_name, args.task)
                print(result[:300] + "..." if len(result) > 300 else result)

        logger.info("Task completed successfully")

    except Exception as e:
        logger.error(f"Error executing task: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()
