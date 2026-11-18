(() => {
  const state = {
    agents: [],
    agent: "autonoma",
    sessionId: localStorage.getItem("autonoma_session") || null,
    busy: false,
  };

  const els = {
    agentList: document.getElementById("agent-list"),
    welcome: document.getElementById("welcome"),
    thread: document.getElementById("thread"),
    form: document.getElementById("chat-form"),
    message: document.getElementById("message"),
    send: document.getElementById("send-btn"),
    activity: document.getElementById("activity"),
    activityText: document.getElementById("activity-text"),
    presence: document.getElementById("presence"),
    presenceLabel: document.getElementById("presence-label"),
    modeLabel: document.getElementById("mode-label"),
    offline: document.getElementById("offline"),
    reset: document.getElementById("reset-btn"),
    starters: document.getElementById("starters"),
  };

  function setPresence(working, label) {
    els.presence.classList.toggle("is-working", working);
    els.presenceLabel.textContent = label;
  }

  function showActivity(text) {
    els.activity.hidden = !text;
    els.activityText.textContent = text || "";
  }

  function eventLabel(event) {
    switch (event.type) {
      case "thinking":
        return `${event.agent || "Autonoma"} is thinking`;
      case "tool_start":
        return `Using ${event.tool}`;
      case "tool_end":
        return event.ok === false ? `${event.tool} failed` : `${event.tool} done`;
      case "specialist":
        return `Calling ${event.specialist}`;
      case "answer":
        return "Composing reply";
      default:
        return event.type;
    }
  }

  function appendMessage({ role, content, agent, events = [] }) {
    els.welcome.hidden = true;
    els.thread.hidden = false;

    const wrap = document.createElement("article");
    wrap.className = `bubble ${role}`;

    const meta = document.createElement("p");
    meta.className = "bubble-meta";
    meta.textContent = role === "user" ? "You" : agent || "Autonoma";

    const body = document.createElement("p");
    body.className = "bubble-body";
    body.textContent = content;

    wrap.append(meta, body);

    if (events.length) {
      const trail = document.createElement("ul");
      trail.className = "event-trail";
      events
        .filter((e) => ["tool_start", "specialist"].includes(e.type))
        .forEach((e) => {
          const li = document.createElement("li");
          li.textContent = eventLabel(e);
          trail.appendChild(li);
        });
      if (trail.childElementCount) wrap.appendChild(trail);
    }

    els.thread.appendChild(wrap);
    els.thread.scrollTop = els.thread.scrollHeight;
  }

  function renderAgents() {
    els.agentList.innerHTML = "";
    state.agents.forEach((agent) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `agent${agent.id === state.agent ? " is-active" : ""}`;
      btn.innerHTML = `<span class="agent-name">${agent.name}</span><span class="agent-role">${agent.role}</span>`;
      btn.addEventListener("click", () => {
        state.agent = agent.id;
        renderAgents();
        els.message.placeholder =
          agent.id === "autonoma"
            ? "Ask Autonoma anything — goals, tasks, questions…"
            : `Talk to ${agent.name}…`;
      });
      els.agentList.appendChild(btn);
    });
  }

  function autosize() {
    els.message.style.height = "auto";
    els.message.style.height = `${Math.min(els.message.scrollHeight, 160)}px`;
  }

  async function loadBootstrap() {
    const [agentsRes, healthRes] = await Promise.all([
      fetch("/api/agents"),
      fetch("/api/health"),
    ]);
    const agentsData = await agentsRes.json();
    const health = await healthRes.json();
    state.agents = agentsData.agents;
    const preferred = state.agents.find((a) => a.default) || state.agents[0];
    state.agent = preferred.id;
    renderAgents();

    if (health.llm_ready) {
      els.modeLabel.textContent = `Connected · ${health.default_model || "model ready"}`;
    } else {
      els.modeLabel.textContent = "No API key · offline workflows available";
      els.offline.checked = true;
    }
  }

  async function sendMessage(text) {
    if (!text || state.busy) return;
    state.busy = true;
    els.send.disabled = true;
    setPresence(true, "On it");
    showActivity("Listening…");

    appendMessage({ role: "user", content: text, agent: "You" });
    els.message.value = "";
    autosize();

    const collected = [];
    try {
      const res = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          agent: state.agent,
          session_id: state.sessionId,
          offline: els.offline.checked,
        }),
      });

      if (!res.ok || !res.body) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Request failed");
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() || "";

        for (const chunk of chunks) {
          const line = chunk.trim();
          if (!line.startsWith("data:")) continue;
          const payload = JSON.parse(line.slice(5).trim());

          if (payload.type === "error") {
            throw new Error(payload.detail || "Something went wrong");
          }
          if (payload.type === "done") {
            state.sessionId = payload.session_id;
            localStorage.setItem("autonoma_session", payload.session_id);
            els.modeLabel.textContent = payload.mode;
            appendMessage({
              role: "assistant",
              content: payload.reply,
              agent: state.agents.find((a) => a.id === payload.agent)?.name || "Autonoma",
              events: collected,
            });
          } else {
            collected.push(payload);
            showActivity(eventLabel(payload));
          }
        }
      }
    } catch (err) {
      appendMessage({
        role: "assistant",
        content: `I hit a snag: ${err.message}`,
        agent: "Autonoma",
      });
    } finally {
      state.busy = false;
      els.send.disabled = false;
      setPresence(false, "Standing by");
      showActivity("");
      els.message.focus();
    }
  }

  els.form.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(els.message.value.trim());
  });

  els.message.addEventListener("input", autosize);
  els.message.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      els.form.requestSubmit();
    }
  });

  els.starters.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-prompt]");
    if (!btn) return;
    sendMessage(btn.dataset.prompt);
  });

  els.reset.addEventListener("click", async () => {
    if (state.sessionId) {
      try {
        await fetch(`/api/session/${state.sessionId}/reset`, { method: "POST" });
      } catch (_) {
        /* empty */
      }
    }
    state.sessionId = null;
    localStorage.removeItem("autonoma_session");
    els.thread.innerHTML = "";
    els.thread.hidden = true;
    els.welcome.hidden = false;
    setPresence(false, "Standing by");
  });

  loadBootstrap().catch((err) => {
    els.modeLabel.textContent = `Could not reach server: ${err.message}`;
  });
})();
