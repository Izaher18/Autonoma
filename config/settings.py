"""Configuration management for the agent framework."""

import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration settings for the agent framework."""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Model Configuration
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview")
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4096"))
    
    # Agent Configuration
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))
    ENABLE_MEMORY: bool = os.getenv("ENABLE_MEMORY", "true").lower() == "true"
    MEMORY_TYPE: str = os.getenv("MEMORY_TYPE", "chromadb")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/agent.log")
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    LOGS_DIR: Path = BASE_DIR / "logs"
    DATA_DIR: Path = BASE_DIR / "data"
    MEMORY_DIR: Path = BASE_DIR / "memory_data"
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all necessary directories exist."""
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.MEMORY_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            print("Warning: No API keys configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
            return False
        return True


# Ensure directories exist
Config.ensure_directories()
