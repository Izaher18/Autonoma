"""FastAPI server for the Autonoma personal assistant UI."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from config.settings import Config
from utils.logging_utils import setup_logging
from agents import (
    AutonomaAgent,
    CodeAssistantAgent,
    DataAnalystAgent,
    ResearchAgent,
)
from core.base_agent import BaseAgent

setup_logging()
logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"

AGENT_CATALOG = [
    {
        "id": "autonoma",
        "name": "Autonoma",
        "role": "Personal assistant",
        "blurb": "Your chief of staff. Remembers context and calls specialists when needed.",
        "default": True,
    },
    {
        "id": "research",
        "name": "Researcher",
        "role": "Research specialist",
        "blurb": "Gathers information and synthesizes findings.",
    },
    {
        "id": "code",
        "name": "Coder",
        "role": "Code specialist",
        "blurb": "Writes, explains, and debugs code.",
    },
    {
        "id": "analyst",
        "name": "Analyst",
        "role": "Data specialist",
        "blurb": "Statistics, trends, and insights from numbers.",
    },
]

app = FastAPI(title="Autonoma", version="0.2.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# session_id -> session dict
_sessions: Dict[str, Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=12000)
    agent: str = "autonoma"
    session_id: Optional[str] = None
    offline: bool = False
    model: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    agent: str
    reply: str
    events: List[Dict[str, Any]]
    mode: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _title_from_history(history: List[Dict[str, Any]]) -> str:
    for message in history:
        if message.get("role") == "user" and message.get("content"):
            text = str(message["content"]).strip().replace("\n", " ")
            return text[:72] + ("…" if len(text) > 72 else "")
    return "New conversation"


def _session_summary(session_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
    history = session.get("history", [])
    return {
        "id": session_id,
        "title": session.get("title") or _title_from_history(history),
        "updated_at": session.get("updated_at") or _now(),
        "message_count": len(history),
        "agent": session.get("last_agent") or "autonoma",
    }


def _make_agent(agent_id: str, offline: bool, model: Optional[str]) -> BaseAgent:
    options = {"use_llm": not offline, "model": model}
    factories = {
        "autonoma": AutonomaAgent,
        "research": ResearchAgent,
        "code": CodeAssistantAgent,
        "analyst": DataAnalystAgent,
    }
    if agent_id not in factories:
        raise HTTPException(status_code=400, detail=f"Unknown agent '{agent_id}'")
    return factories[agent_id](**options)


def _get_session(session_id: Optional[str]) -> str:
    if session_id and session_id in _sessions:
        return session_id
    new_id = session_id or str(uuid.uuid4())
    _sessions[new_id] = {
        "agents": {},
        "history": [],
        "title": "New conversation",
        "updated_at": _now(),
        "last_agent": "autonoma",
        "archived": False,
    }
    return new_id


def _agent_for(
    session_id: str, agent_id: str, offline: bool, model: Optional[str]
) -> BaseAgent:
    session = _sessions[session_id]
    key = f"{agent_id}:{'off' if offline else 'on'}:{model or ''}"
    agents: Dict[str, BaseAgent] = session["agents"]
    if key not in agents:
        agents[key] = _make_agent(agent_id, offline, model)
    return agents[key]


def _record_turn(
    session_id: str,
    agent_id: str,
    user_message: str,
    reply: str,
    events: List[Dict[str, Any]],
) -> None:
    session = _sessions[session_id]
    session["history"].append({"role": "user", "content": user_message, "agent": agent_id})
    session["history"].append(
        {"role": "assistant", "content": reply, "agent": agent_id, "events": events}
    )
    if session.get("title") in (None, "", "New conversation"):
        session["title"] = _title_from_history(session["history"])
    session["updated_at"] = _now()
    session["last_agent"] = agent_id
    session["archived"] = False


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
async def health():
    has_key = bool(Config.OPENAI_API_KEY or Config.ANTHROPIC_API_KEY)
    return {
        "ok": True,
        "llm_ready": has_key,
        "default_model": Config.DEFAULT_MODEL
        or (
            Config.OPENAI_DEFAULT_MODEL
            if Config.OPENAI_API_KEY
            else Config.ANTHROPIC_DEFAULT_MODEL if Config.ANTHROPIC_API_KEY else None
        ),
    }


@app.get("/api/agents")
async def list_agents():
    return {"agents": AGENT_CATALOG}


@app.get("/api/sessions")
async def list_sessions():
    """List conversations kept on this server process (newest first)."""
    items = [
        _session_summary(session_id, session)
        for session_id, session in _sessions.items()
        if session.get("history")
    ]
    items.sort(key=lambda item: item["updated_at"], reverse=True)
    return {"sessions": items}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        **_session_summary(session_id, session),
        "history": session.get("history", []),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = _get_session(req.session_id)
    agent = _agent_for(session_id, req.agent, req.offline, req.model)
    events: List[Dict[str, Any]] = []

    def on_event(event: str, payload: Dict[str, Any]):
        events.append({"type": event, **payload})

    agent.on_event = on_event
    try:
        reply = await asyncio.to_thread(agent.execute, req.message.strip())
    except Exception as e:
        logger.exception("Chat failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        agent.on_event = None

    mode = f"model {agent.llm.model}" if agent.llm else "offline"
    _record_turn(session_id, req.agent, req.message, reply, events)
    return ChatResponse(
        session_id=session_id,
        agent=req.agent,
        reply=reply,
        events=events,
        mode=mode,
    )


@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    """Server-sent events: activity trail, then the final reply."""
    session_id = _get_session(req.session_id)
    agent = _agent_for(session_id, req.agent, req.offline, req.model)
    queue: asyncio.Queue = asyncio.Queue()
    events: List[Dict[str, Any]] = []

    def on_event(event: str, payload: Dict[str, Any]):
        item = {"type": event, **payload}
        events.append(item)
        queue.put_nowait(item)

    async def run():
        agent.on_event = on_event
        try:
            reply = await asyncio.to_thread(agent.execute, req.message.strip())
            mode = f"model {agent.llm.model}" if agent.llm else "offline"
            _record_turn(session_id, req.agent, req.message, reply, events)
            await queue.put(
                {
                    "type": "done",
                    "session_id": session_id,
                    "agent": req.agent,
                    "reply": reply,
                    "mode": mode,
                    "title": _sessions[session_id].get("title"),
                }
            )
        except Exception as e:
            logger.exception("Streamed chat failed")
            await queue.put({"type": "error", "detail": str(e)})
        finally:
            agent.on_event = None
            await queue.put(None)

    async def event_generator():
        task = asyncio.create_task(run())
        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                yield f"data: {json.dumps(item, default=str)}\n\n"
        finally:
            await task

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/sessions/{session_id}/archive")
async def archive_session(session_id: str):
    """Keep the conversation in history; stop using it as the active thread."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session["archived"] = True
    session["updated_at"] = _now()
    return {"ok": True, "session": _session_summary(session_id, session)}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    del _sessions[session_id]
    return {"ok": True}


@app.post("/api/session/{session_id}/reset")
async def reset_session(session_id: str):
    """Legacy: clear agents in-place. Prefer archive + new session for history."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    for agent in session["agents"].values():
        agent.reset()
    session["history"] = []
    session["title"] = "New conversation"
    session["updated_at"] = _now()
    return {"ok": True}


def main():
    import uvicorn

    uvicorn.run("web.app:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
