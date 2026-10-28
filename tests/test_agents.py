"""Tests for the built-in agents."""

from agents import CodeAssistantAgent, DataAnalystAgent, ResearchAgent


def test_research_agent_execute():
    """Research agent runs its search/analyze/extract pipeline."""
    result = ResearchAgent().execute("AI agents")
    assert "Research Results for: AI agents" in result
    assert "Key Facts" in result


def test_code_assistant_generates_code():
    """Code assistant routes 'generate' requests to code generation."""
    result = CodeAssistantAgent().execute("Generate a fibonacci function")
    assert "Generated Code" in result
    assert "def main()" in result


def test_data_analyst_statistics():
    """Statistics are computed correctly."""
    stats = DataAnalystAgent().analyze_statistics([1, 2, 3, 4])
    assert stats["mean"] == 2.5
    assert stats["median"] == 2.5
    assert stats["range"] == 3


def test_data_analyst_trends():
    """Monotonic increasing data is detected as upward."""
    trends = DataAnalystAgent().identify_trends([1, 2, 3, 4, 5])
    assert trends["trend"] == "upward"


def test_clean_data_handles_unhashable_items():
    """clean_data dedupes dicts/lists without raising TypeError."""
    report = DataAnalystAgent().clean_data([{"a": 1}, None, {"a": 1}, [1, 2], 3])
    assert report["removed_nulls"] == 1
    assert report["removed_duplicates"] == 1
    assert report["cleaned_data"] == [{"a": 1}, [1, 2], 3]
