"""Logging utilities for the agent framework."""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from config.settings import Config


def setup_logging(
    name: Optional[str] = None, level: Optional[str] = None, log_file: Optional[str] = None
) -> logging.Logger:
    """Setup logging configuration.

    Args:
        name: Logger name (defaults to the root logger, so all modules inherit it)
        level: Logging level
        log_file: Path to log file

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    # Set level
    log_level = getattr(logging, (level or Config.LOG_LEVEL).upper())
    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file or Config.LOG_FILE:
        file_path = Path(log_file or Config.LOG_FILE)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            file_path, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
