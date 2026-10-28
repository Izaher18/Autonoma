"""Test configuration."""

import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Config  # noqa: E402


@pytest.fixture(autouse=True)
def no_api_keys(monkeypatch):
    """Keep tests offline even when a developer's .env has real API keys."""
    monkeypatch.setattr(Config, "OPENAI_API_KEY", "")
    monkeypatch.setattr(Config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(Config, "DEFAULT_MODEL", "")
