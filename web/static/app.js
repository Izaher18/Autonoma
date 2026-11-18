(() => {
  const STORE_KEY = "autonoma_conversations";
  const ACTIVE_KEY = "autonoma_session";
  const PANEL_KEY = "autonoma_history_open";

  const state = {
    agents: [],
    agent: "autonoma",
    sessionId: localStorage.getItem(ACTIVE_KEY) || null,
    messages: [],
    conversations: [],
    busy: false,
    historyOpen: localStorage.getItem(PANEL_KEY) !== "0",
  };

  const els = {
    frame: document.querySelector(".frame"),
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
    historyPanel: document.getElementById("history-panel"),
    historyList: document.getElementById("history-list"),
    historyEmpty: document.getElementById("history-empty"),
    historyToggle: document.getElementById("history-toggle"),
    activeAgentLabel: document.getElementById("active-agent-label"),
  };

  function loadStore() {
    try {
      const raw = JSON.parse(localStorage.getItem(STORE_KEY) || "[]");
      return Array.isArray(raw) ? raw : [];
    } catch (_) {
      return [];
    }
  }

  function saveStore(list) {
    localStorage.setItem(STORE_KEY, JSON.stringify(list.slice(0, 40)));
    state.conversations = list.slice(0, 40);
  }

  function titleFromMessages(messages) {
    const first = messages.find((m) => m.role === "user" && m.content);
    if (!first) return "New conversation";
    const text = String(first.content).trim().replace(/\s+/g, " ");
    return text.length > 72 ? `${text.slice(0, 72)}…` : text;
  }

  function agentName(id) {
    return state.agents.find((a) => a.id === id)?.name || id || "Autonoma";
  }

  function formatWhen(iso) {
    if (!iso) return "";
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return "";
    return date.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  }

  function persistCurrent() {
    if (!state.sessionId || !state.messages.length) return;
    const list = loadStore().filter((c) => c.id !== state.sessionId);
    list.unshift({
      id: state.sessionId,
      title: titleFromMessages(state.messages),
      agent: state.agent,
      updatedAt: new Date().toISOString(),
      messages: state.messages,
    });
    saveStore(list);
    renderHistory();
  }

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

  function renderThread() {
    els.thread.innerHTML = "";
    if (!state.messages.length) {
      els.welcome.hidden = false;
      els.thread.hidden = true;
      return;
    }
    els.welcome.hidden = true;
    els.thread.hidden = false;
    state.messages.forEach((message) => {
      const wrap = document.createElement("article");
      wrap.className = `bubble ${message.role}`;

      const meta = document.createElement("p");
      meta.className = "bubble-meta";
      meta.textContent =
        message.role === "user" ? "You" : agentName(message.agent) || "Autonoma";

      const body = document.createElement("p");
      body.className = "bubble-body";
      body.textContent = message.content;

      wrap.append(meta, body);

      if (message.events?.length) {
        const trail = document.createElement("ul");
        trail.className = "event-trail";
        message.events
          .filter((e) => ["tool_start", "specialist"].includes(e.type))
          .forEach((e) => {
            const li = document.createElement("li");
            li.textContent = eventLabel(e);
            trail.appendChild(li);
          });
        if (trail.childElementCount) wrap.appendChild(trail);
      }

      els.thread.appendChild(wrap);
    });
    els.thread.scrollTop = els.thread.scrollHeight;
  }

  function appendMessage(message) {
    state.messages.push(message);
    renderThread();
    persistCurrent();
  }

  function renderHistory() {
    const list = loadStore();
    state.conversations = list;
    els.historyList.querySelectorAll(".history-item-row").forEach((node) => node.remove());
    els.historyEmpty.hidden = list.length > 0;

    list.forEach((conv) => {
      const row = document.createElement("div");
      row.className = "history-item-row";

      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `history-item${conv.id === state.sessionId ? " is-active" : ""}`;
      btn.innerHTML = `
        <span class="history-item-title"></span>
        <span class="history-item-meta"></span>
      `;
      btn.querySelector(".history-item-title").textContent = conv.title || "Conversation";
      btn.querySelector(".history-item-meta").textContent = [
        agentName(conv.agent),
        formatWhen(conv.updatedAt),
      ]
        .filter(Boolean)
        .join(" · ");
      btn.addEventListener("click", () => openConversation(conv.id));

      const del = document.createElement("button");
      del.type = "button";
      del.className = "history-delete";
      del.title = "Remove from history";
      del.textContent = "✕";
      del.addEventListener("click", (e) => {
        e.stopPropagation();
        deleteConversation(conv.id);
      });

      row.append(btn, del);
      els.historyList.appendChild(row);
    });
  }

  function setHistoryOpen(open) {
    state.historyOpen = open;
    els.historyPanel.classList.toggle("is-open", open);
    els.frame.classList.toggle("history-collapsed", !open);
    els.historyToggle.setAttribute("aria-expanded", open ? "true" : "false");
    localStorage.setItem(PANEL_KEY, open ? "1" : "0");
  }

  function openConversation(id) {
    const conv = loadStore().find((c) => c.id === id);
    if (!conv) return;
    persistCurrent();
    state.sessionId = conv.id;
    state.messages = Array.isArray(conv.messages) ? [...conv.messages] : [];
    localStorage.setItem(ACTIVE_KEY, id);
    setActiveAgent(conv.agent || state.agent);
    renderAgents();
    renderThread();
    renderHistory();
    setPresence(false, "Standing by");
    if (window.matchMedia("(max-width: 960px)").matches) {
      setHistoryOpen(false);
    }
  }

  function deleteConversation(id) {
    const next = loadStore().filter((c) => c.id !== id);
    saveStore(next);
    fetch(`/api/sessions/${id}`, { method: "DELETE" }).catch(() => {});
    if (state.sessionId === id) {
      startNewConversation({ skipArchive: true });
    } else {
      renderHistory();
    }
  }

  async function startNewConversation({ skipArchive = false } = {}) {
    if (!skipArchive && state.sessionId && state.messages.length) {
      persistCurrent();
      fetch(`/api/sessions/${state.sessionId}/archive`, { method: "POST" }).catch(() => {});
    }
    state.sessionId = null;
    state.messages = [];
    localStorage.removeItem(ACTIVE_KEY);
    renderThread();
    renderHistory();
    setPresence(false, "Standing by");
  }

  function setActiveAgent(agentId) {
    const agent = state.agents.find((a) => a.id === agentId) || state.agents[0];
    if (!agent) return;
    state.agent = agent.id;
    els.activeAgentLabel.textContent = agent.role;
    els.message.placeholder =
      agent.id === "autonoma"
        ? "Ask Autonoma anything — goals, tasks, questions…"
        : `Talk to ${agent.name}…`;
  }

  function renderAgents() {
    els.agentList.innerHTML = "";
    state.agents.forEach((agent) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `agent${agent.id === state.agent ? " is-active" : ""}`;
      btn.innerHTML = `<span class="agent-name">${agent.name}</span><span class="agent-role">${agent.role}</span>`;
      btn.addEventListener("click", () => {
        setActiveAgent(agent.id);
        renderAgents();
        persistCurrent();
        renderHistory();
      });
      els.agentList.appendChild(btn);
    });
    const active = state.agents.find((a) => a.id === state.agent);
    if (active) els.activeAgentLabel.textContent = active.role;
  }

  function autosize() {
    els.message.style.height = "auto";
    els.message.style.height = `${Math.min(els.message.scrollHeight, 160)}px`;
  }

  async function restoreActive() {
    if (!state.sessionId) return;
    const local = loadStore().find((c) => c.id === state.sessionId);
    if (local?.messages?.length) {
      state.messages = [...local.messages];
      state.agent = local.agent || state.agent;
      renderThread();
      return;
    }
    try {
      const res = await fetch(`/api/sessions/${state.sessionId}`);
      if (!res.ok) return;
      const data = await res.json();
      state.messages = (data.history || []).map((m) => ({
        role: m.role,
        content: m.content,
        agent: m.agent,
        events: m.events || [],
      }));
      state.agent = data.agent || state.agent;
      persistCurrent();
      renderThread();
    } catch (_) {
      /* empty */
    }
  }

  async function loadBootstrap() {
    const [agentsRes, healthRes] = await Promise.all([
      fetch("/api/agents"),
      fetch("/api/health"),
    ]);
    const agentsData = await agentsRes.json();
    const health = await healthRes.json();
    state.agents = agentsData.agents;
    if (!state.agents.some((a) => a.id === state.agent)) {
      const preferred = state.agents.find((a) => a.default) || state.agents[0];
      state.agent = preferred.id;
    }
    setActiveAgent(state.agent);
    renderAgents();
    setHistoryOpen(state.historyOpen);
    renderHistory();
    await restoreActive();

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
            localStorage.setItem(ACTIVE_KEY, payload.session_id);
            els.modeLabel.textContent = payload.mode;
            appendMessage({
              role: "assistant",
              content: payload.reply,
              agent: payload.agent,
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
        agent: "autonoma",
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

  els.reset.addEventListener("click", () => startNewConversation());
  els.historyToggle.addEventListener("click", () => setHistoryOpen(!state.historyOpen));

  loadBootstrap().catch((err) => {
    els.modeLabel.textContent = `Could not reach server: ${err.message}`;
  });
})();
