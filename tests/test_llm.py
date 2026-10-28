"""Tests for LLM clients and the agent tool-calling loop (no network calls)."""

from types import SimpleNamespace
from typing import Dict, List, Optional

import pytest

from agents import CodeAssistantAgent, DataAnalystAgent, ResearchAgent
from config.settings import Config
from core.base_agent import BaseAgent
from core.llm import (
    AnthropicClient,
    LLMClient,
    LLMResponse,
    OpenAIClient,
    ToolCall,
    create_llm,
    to_anthropic_messages,
    to_openai_messages,
)
from core.tool_registry import tool, tool_schema


class ScriptedLLM(LLMClient):
    """Returns pre-defined responses and records every request."""

    def __init__(self, responses: List[LLMResponse]):
        super().__init__("scripted-model")
        self.responses = list(responses)
        self.requests: List[Dict] = []

    def chat(self, system, messages, tools=None, temperature=None, max_tokens=4096):
        self.requests.append(
            {"system": system, "messages": [dict(m) for m in messages], "tools": tools}
        )
        return self.responses.pop(0)


class CalculatorAgent(BaseAgent):
    """Agent with one real tool and one hidden tool."""

    def __init__(self, llm: Optional[LLMClient] = None):
        super().__init__(name="Calculator", llm=llm)

    @tool(description="Add two numbers")
    def add(self, a: int, b: int = 0) -> int:
        """Add numbers.

        Args:
            a: First number
            b: Second number
        """
        return a + b

    @tool(description="Hidden placeholder", expose_to_llm=False)
    def secret(self) -> str:
        return "should never run"


def test_tool_loop_runs_tool_then_answers():
    llm = ScriptedLLM(
        [
            LLMResponse(tool_calls=[ToolCall(id="c1", name="add", arguments={"a": 2, "b": 3})]),
            LLMResponse(text="The answer is 5"),
        ]
    )
    agent = CalculatorAgent(llm=llm)

    assert agent.execute("what is 2+3?") == "The answer is 5"

    tool_result = llm.requests[1]["messages"][-1]
    assert tool_result == {"role": "tool", "tool_call_id": "c1", "content": "5", "is_error": False}
    assert [m.role for m in agent.conversation_history] == ["user", "assistant"]
    assert agent.conversation_history[-1].metadata["tools_used"] == ["add"]


def test_tool_loop_reports_errors_to_model():
    llm = ScriptedLLM(
        [
            LLMResponse(
                tool_calls=[
                    ToolCall(id="c1", name="secret", arguments={}),
                    ToolCall(id="c2", name="add", arguments={"wrong": 1}),
                ]
            ),
            LLMResponse(text="Sorry"),
        ]
    )
    agent = CalculatorAgent(llm=llm)
    agent.execute("break things")

    hidden, bad_args = llm.requests[1]["messages"][-2:]
    assert hidden["is_error"] and "Unknown tool 'secret'" in hidden["content"]
    assert bad_args["is_error"] and bad_args["content"].startswith("Error:")


def test_tool_loop_stops_at_max_iterations():
    call = ToolCall(id="c", name="add", arguments={"a": 1})
    llm = ScriptedLLM([LLMResponse(tool_calls=[call]) for _ in range(3)])
    agent = CalculatorAgent(llm=llm)
    agent.config.max_iterations = 3

    result = agent.execute("loop forever")

    assert "Stopped after 3" in result
    assert len(llm.requests) == 3


def test_previous_turns_are_sent_as_context():
    llm = ScriptedLLM([LLMResponse(text="first"), LLMResponse(text="second")])
    agent = CalculatorAgent(llm=llm)
    agent.execute("hello")
    agent.execute("again")

    assert llm.requests[1]["messages"] == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "first"},
        {"role": "user", "content": "again"},
    ]


def test_only_exposed_tools_are_sent():
    agent = CalculatorAgent(llm=ScriptedLLM([]))
    assert [schema["name"] for schema in agent.get_tool_schemas()] == ["add"]


def test_tool_schema_from_signature_and_docstring():
    schema = tool_schema("add", CalculatorAgent(llm=ScriptedLLM([])).add)
    assert schema == {
        "name": "add",
        "description": "Add two numbers",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "First number"},
                "b": {"type": "integer", "description": "Second number", "default": 0},
            },
            "required": ["a"],
        },
    }


def test_tool_schema_handles_collections():
    schema = tool_schema("clean_data", DataAnalystAgent(use_llm=False).clean_data)
    assert schema["parameters"]["properties"]["data"]["type"] == "array"
    schema = tool_schema("stats", DataAnalystAgent(use_llm=False).analyze_statistics)
    assert schema["parameters"]["properties"]["data"]["items"] == {"type": "number"}


def test_builtin_agents_fall_back_to_offline_without_keys():
    for agent_cls in (ResearchAgent, CodeAssistantAgent, DataAnalystAgent):
        agent = agent_cls()
        assert agent.llm is None
        assert agent.execute("generate an analysis")


def test_base_agent_without_offline_mode_explains_how_to_fix():
    class Bare(BaseAgent):
        pass

    with pytest.raises(NotImplementedError, match="OPENAI_API_KEY"):
        Bare(name="Bare").execute("hi")


TOOL_TURN = [
    {"role": "user", "content": "hi"},
    {
        "role": "assistant",
        "content": "checking",
        "tool_calls": [
            ToolCall(id="a", name="add", arguments={"a": 1}),
            ToolCall(id="b", name="add", arguments={"a": 2}),
        ],
    },
    {"role": "tool", "tool_call_id": "a", "content": "1", "is_error": False},
    {"role": "tool", "tool_call_id": "b", "content": "Error: boom", "is_error": True},
]


def test_openai_message_format():
    converted = to_openai_messages("sys", TOOL_TURN)
    assert converted[0] == {"role": "system", "content": "sys"}
    assert converted[2]["tool_calls"][0] == {
        "id": "a",
        "type": "function",
        "function": {"name": "add", "arguments": '{"a": 1}'},
    }
    assert converted[3] == {"role": "tool", "tool_call_id": "a", "content": "1"}


def test_anthropic_message_format_merges_tool_results():
    converted = to_anthropic_messages(TOOL_TURN)
    assert len(converted) == 3
    assert converted[1]["content"] == [
        {"type": "text", "text": "checking"},
        {"type": "tool_use", "id": "a", "name": "add", "input": {"a": 1}},
        {"type": "tool_use", "id": "b", "name": "add", "input": {"a": 2}},
    ]
    assert converted[2] == {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": "a", "content": "1"},
            {"type": "tool_result", "tool_use_id": "b", "content": "Error: boom", "is_error": True},
        ],
    }


def _openai_completion(content=None, tool_calls=None):
    message = SimpleNamespace(content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def test_openai_client_parses_tool_calls_and_retries_without_temperature():
    class TemperatureRejected(Exception):
        status_code = 400

    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        if "temperature" in kwargs:
            raise TemperatureRejected("Unsupported value: 'temperature'")
        function = SimpleNamespace(name="add", arguments='{"a": 4}')
        return _openai_completion(
            tool_calls=[SimpleNamespace(id="t1", type="function", function=function)]
        )

    fake = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    client = OpenAIClient("gpt-test", client=fake)
    tools = [{"name": "add", "description": "Add", "parameters": {"type": "object"}}]

    response = client.chat("sys", [{"role": "user", "content": "hi"}], tools, temperature=0.5)

    assert response.tool_calls == [ToolCall(id="t1", name="add", arguments={"a": 4})]
    assert "temperature" in calls[0] and "temperature" not in calls[1]
    assert calls[1]["max_completion_tokens"] == 4096
    assert calls[1]["tools"][0]["function"]["name"] == "add"

    client.chat("sys", [{"role": "user", "content": "again"}], temperature=0.5)
    assert "temperature" not in calls[2]


def test_anthropic_client_parses_response():
    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            content=[
                SimpleNamespace(type="text", text="Let me add. "),
                SimpleNamespace(type="tool_use", id="u1", name="add", input={"a": 1}),
            ]
        )

    client = AnthropicClient(
        "claude-test", client=SimpleNamespace(messages=SimpleNamespace(create=create))
    )
    tools = [{"name": "add", "description": "Add", "parameters": {"type": "object"}}]

    response = client.chat("sys", [{"role": "user", "content": "hi"}], tools, temperature=0.9)

    assert response.text == "Let me add. "
    assert response.tool_calls == [ToolCall(id="u1", name="add", arguments={"a": 1})]
    assert captured["system"] == "sys"
    assert captured["tools"][0]["input_schema"] == {"type": "object"}
    assert "temperature" not in captured


def test_placeholder_api_keys_are_ignored(monkeypatch):
    from config.settings import _api_key

    monkeypatch.setenv("OPENAI_API_KEY", "your_openai_api_key_here")
    assert _api_key("OPENAI_API_KEY") == ""
    monkeypatch.setenv("OPENAI_API_KEY", " sk-real ")
    assert _api_key("OPENAI_API_KEY") == "sk-real"


def test_create_llm_without_keys_returns_none():
    assert create_llm() is None


def test_create_llm_picks_provider_from_available_key(monkeypatch):
    monkeypatch.setattr(Config, "ANTHROPIC_API_KEY", "sk-ant-test")
    llm = create_llm()
    assert isinstance(llm, AnthropicClient)
    assert llm.model == Config.ANTHROPIC_DEFAULT_MODEL

    monkeypatch.setattr(Config, "OPENAI_API_KEY", "sk-test")
    llm = create_llm()
    assert isinstance(llm, OpenAIClient)
    assert llm.model == Config.OPENAI_DEFAULT_MODEL


def test_create_llm_respects_model_and_requires_matching_key(monkeypatch):
    monkeypatch.setattr(Config, "OPENAI_API_KEY", "sk-test")
    assert create_llm("claude-sonnet-5-5") is None
    assert create_llm("gpt-5.5").model == "gpt-5.5"
