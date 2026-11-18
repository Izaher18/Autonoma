"""Tests for the Autonoma personal assistant and web API."""

from core.llm import LLMClient, LLMResponse, ToolCall
from agents.autonoma import AutonomaAgent


class ScriptedLLM(LLMClient):
    def __init__(self, responses):
        super().__init__("scripted")
        self.responses = list(responses)

    def chat(self, system, messages, tools=None, temperature=None, max_tokens=4096):
        return self.responses.pop(0)


def test_autonoma_offline_routes_to_specialists():
    agent = AutonomaAgent(use_llm=False)
    result = agent.execute("mean and trend of these numbers")
    assert "Data Analysis" in result or "Statistical" in result or "trend" in result.lower()


def test_autonoma_remembers_offline():
    agent = AutonomaAgent(use_llm=False)
    reply = agent.execute("Remember that I like Python")
    assert "saved" in reply.lower() or "Remembered" in reply
    assert agent.memory.search("Python")


def test_autonoma_delegates_via_llm_tools():
    llm = ScriptedLLM(
        [
            LLMResponse(
                tool_calls=[
                    ToolCall(
                        id="1",
                        name="ask_analyst",
                        arguments={"task": "mean of 1,2,3"},
                    )
                ]
            ),
            LLMResponse(text="The mean is 2."),
        ]
    )
    events = []
    agent = AutonomaAgent(llm=llm)
    agent.on_event = lambda event, payload: events.append({"type": event, **payload})

    assert agent.execute("average these") == "The mean is 2."
    assert any(e["type"] == "specialist" for e in events)
    assert any(e.get("tool") == "ask_analyst" for e in events)


def test_web_api_offline_chat():
    from fastapi.testclient import TestClient
    from web.app import app

    client = TestClient(app)
    health = client.get("/api/health")
    assert health.status_code == 200

    agents = client.get("/api/agents").json()["agents"]
    assert agents[0]["id"] == "autonoma"

    res = client.post(
        "/api/chat",
        json={"message": "hello there", "agent": "autonoma", "offline": True},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["reply"]
    assert body["mode"] == "offline"
    assert body["session_id"]


def test_web_sessions_persist_across_new_conversation():
    from fastapi.testclient import TestClient
    from web import app as web_app

    web_app._sessions.clear()
    client = TestClient(web_app.app)

    first = client.post(
        "/api/chat",
        json={"message": "Remember I like Python", "agent": "autonoma", "offline": True},
    ).json()
    session_id = first["session_id"]

    listed = client.get("/api/sessions").json()["sessions"]
    assert any(item["id"] == session_id for item in listed)

    detail = client.get(f"/api/sessions/{session_id}").json()
    assert detail["history"][0]["content"] == "Remember I like Python"
    assert "Python" in detail["title"]

    archived = client.post(f"/api/sessions/{session_id}/archive")
    assert archived.status_code == 200

    # Starting another chat creates a second conversation; the first stays listed.
    second = client.post(
        "/api/chat",
        json={"message": "mean of 1, 2, 3", "agent": "analyst", "offline": True},
    ).json()
    assert second["session_id"] != session_id
    ids = {item["id"] for item in client.get("/api/sessions").json()["sessions"]}
    assert session_id in ids
    assert second["session_id"] in ids

    deleted = client.delete(f"/api/sessions/{session_id}")
    assert deleted.status_code == 200
    ids = {item["id"] for item in client.get("/api/sessions").json()["sessions"]}
    assert session_id not in ids
