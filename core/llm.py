"""LLM provider clients with native tool calling.

Agents talk to every provider through one neutral message format:

- ``{"role": "user", "content": str}``
- ``{"role": "assistant", "content": str, "tool_calls": [ToolCall, ...]}`` (``tool_calls`` optional)
- ``{"role": "tool", "tool_call_id": str, "content": str, "is_error": bool}``

Tools are ``{"name": str, "description": str, "parameters": <JSON schema object>}``.
Each client converts these to its provider's wire format.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from config.settings import Config

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """A tool invocation requested by the model."""

    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """A single model turn: optional text plus any requested tool calls."""

    text: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)


class LLMClient:
    """Provider-neutral chat interface."""

    provider = ""

    def __init__(self, model: str):
        self.model = model

    def chat(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Send one request to the model and return its reply."""
        raise NotImplementedError


def _parse_arguments(raw: Optional[str]) -> Dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning(f"Model returned invalid JSON tool arguments: {raw!r}")
        return {}
    return parsed if isinstance(parsed, dict) else {}


def to_openai_messages(system: str, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert neutral messages to OpenAI Chat Completions format."""
    converted: List[Dict[str, Any]] = [{"role": "system", "content": system}] if system else []
    for message in messages:
        if message["role"] == "tool":
            converted.append(
                {
                    "role": "tool",
                    "tool_call_id": message["tool_call_id"],
                    "content": message["content"],
                }
            )
        elif message.get("tool_calls"):
            converted.append(
                {
                    "role": "assistant",
                    "content": message.get("content") or None,
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.name,
                                "arguments": json.dumps(call.arguments),
                            },
                        }
                        for call in message["tool_calls"]
                    ],
                }
            )
        else:
            converted.append({"role": message["role"], "content": message["content"]})
    return converted


def to_anthropic_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert neutral messages to Anthropic Messages format.

    Anthropic expects all results for one assistant turn in a single user message,
    so consecutive tool results are merged.
    """
    converted: List[Dict[str, Any]] = []
    for message in messages:
        if message["role"] == "tool":
            block: Dict[str, Any] = {
                "type": "tool_result",
                "tool_use_id": message["tool_call_id"],
                "content": message["content"],
            }
            if message.get("is_error"):
                block["is_error"] = True
            previous = converted[-1] if converted else None
            if (
                previous
                and previous["role"] == "user"
                and isinstance(previous["content"], list)
                and previous["content"][0].get("type") == "tool_result"
            ):
                previous["content"].append(block)
            else:
                converted.append({"role": "user", "content": [block]})
        elif message.get("tool_calls"):
            content: List[Dict[str, Any]] = []
            if message.get("content"):
                content.append({"type": "text", "text": message["content"]})
            content.extend(
                {"type": "tool_use", "id": call.id, "name": call.name, "input": call.arguments}
                for call in message["tool_calls"]
            )
            converted.append({"role": "assistant", "content": content})
        else:
            converted.append({"role": message["role"], "content": message["content"]})
    return converted


class OpenAIClient(LLMClient):
    """OpenAI Chat Completions client."""

    provider = "openai"

    def __init__(self, model: str, api_key: Optional[str] = None, client: Any = None):
        super().__init__(model)
        if client is None:
            from openai import OpenAI

            client = OpenAI(api_key=api_key or Config.OPENAI_API_KEY)
        self._client = client
        self._send_temperature = True

    def chat(self, system, messages, tools=None, temperature=None, max_tokens=4096):
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": to_openai_messages(system, messages),
            "max_completion_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"],
                    },
                }
                for tool in tools
            ]
        if temperature is not None and self._send_temperature:
            kwargs["temperature"] = temperature

        try:
            completion = self._client.chat.completions.create(**kwargs)
        except Exception as e:
            # Reasoning models only accept the default temperature.
            rejected_temperature = (
                "temperature" in kwargs
                and getattr(e, "status_code", None) == 400
                and "temperature" in str(e)
            )
            if not rejected_temperature:
                raise
            logger.info(f"Model {self.model} does not support temperature; retrying without it")
            self._send_temperature = False
            del kwargs["temperature"]
            completion = self._client.chat.completions.create(**kwargs)

        message = completion.choices[0].message
        tool_calls = [
            ToolCall(
                id=call.id,
                name=call.function.name,
                arguments=_parse_arguments(call.function.arguments),
            )
            for call in (message.tool_calls or [])
            if call.type == "function"
        ]
        return LLMResponse(text=message.content or "", tool_calls=tool_calls)


class AnthropicClient(LLMClient):
    """Anthropic Messages client. Anthropic models do not take a temperature."""

    provider = "anthropic"

    def __init__(self, model: str, api_key: Optional[str] = None, client: Any = None):
        super().__init__(model)
        if client is None:
            from anthropic import Anthropic

            client = Anthropic(api_key=api_key or Config.ANTHROPIC_API_KEY)
        self._client = client

    def chat(self, system, messages, tools=None, temperature=None, max_tokens=4096):
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "messages": to_anthropic_messages(messages),
            "max_tokens": max_tokens,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": tool["parameters"],
                }
                for tool in tools
            ]

        response = self._client.messages.create(**kwargs)

        text = "".join(block.text for block in response.content if block.type == "text")
        tool_calls = [
            ToolCall(id=block.id, name=block.name, arguments=dict(block.input or {}))
            for block in response.content
            if block.type == "tool_use"
        ]
        return LLMResponse(text=text, tool_calls=tool_calls)


def provider_for_model(model: str) -> str:
    """Infer the provider from a model name."""
    return "anthropic" if model.startswith("claude") else "openai"


def create_llm(model: Optional[str] = None) -> Optional[LLMClient]:
    """Create a client for ``model``, or pick a default based on available API keys.

    Returns None when no usable API key is configured, so agents can run offline.
    """
    model = model or Config.DEFAULT_MODEL
    if not model:
        if Config.OPENAI_API_KEY:
            model = Config.OPENAI_DEFAULT_MODEL
        elif Config.ANTHROPIC_API_KEY:
            model = Config.ANTHROPIC_DEFAULT_MODEL
        else:
            return None

    provider = provider_for_model(model)
    api_key = Config.ANTHROPIC_API_KEY if provider == "anthropic" else Config.OPENAI_API_KEY
    if not api_key:
        logger.warning(f"Model {model} needs {provider.upper()}_API_KEY; running offline")
        return None

    try:
        if provider == "anthropic":
            return AnthropicClient(model, api_key=api_key)
        return OpenAIClient(model, api_key=api_key)
    except ImportError:
        logger.warning(f"The '{provider}' package is not installed; running offline")
        return None
