"""Main entry point for running agents."""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from utils.logging_utils import setup_logging
from config.settings import Config
from agents import ResearchAgent, CodeAssistantAgent, DataAnalystAgent
from core.agent_manager import AgentManager

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Agentic AI Framework")
    parser.add_argument(
        "--agent",
        choices=["research", "code", "analyst", "multi"],
        default="research",
        help="Agent type to run",
    )
    parser.add_argument("--task", type=str, required=True, help="Task description for the agent")
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

    if args.offline:
        logger.info("Offline mode: using scripted workflows, no LLM calls")
    elif not Config.validate():
        logger.warning("No API keys set; running scripted offline workflows instead of an LLM")

    agent_options = {"model": args.model, "use_llm": not args.offline}
    logger.info(f"Starting {args.agent} agent with task: {args.task}")

    try:
        if args.agent == "research":
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

            # Execute task with all agents
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
