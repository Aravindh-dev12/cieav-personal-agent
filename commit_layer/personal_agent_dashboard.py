"""
CIEAV Personal Agent Web Dashboard & Workspace Service (Port 6796).
===================================================================
A self-hosted, sovereign, Dots-style personal-agent web dashboard running on
http://127.0.0.1:6796 with Two-Phase Commit (2PC) authority and cryptographic receipts.

Key Capabilities:
1. Personal-Agent Web Dashboard:
   - Real-time task threads & multi-agent conversations
   - Persistent memory vault & preferences (MemFS / SOUL)
   - Multi-agent squads (Researcher, Product Team, Coder, Sentinel, Atlas)
   - Scheduled routines & 08:00 AM morning intelligence
   - Live 2PC authority, spend caps, and Ed25519 hash-chain receipts with /undo
2. BYOM / Local Model Settings:
   - Configurable for local CPU Qwen GGUF, Ollama, vLLM, or external endpoints
3. Background Daemon Runner:
   - Autonomous background service lifecycle (start, stop, status)
"""

from __future__ import annotations
import os
import sys
import json
import time
import socket
import logging
import threading
import webbrowser
import subprocess
from typing import Any, Dict, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

from commit_layer import gateway, receipts
from commit_layer.workspace import get_workspace_root, get_data_dir
from commit_layer.memory_hive import memory_hive
from commit_layer.tools.morning_briefing_agent import morning_briefing_agent
from commit_layer.autonomous_workforce import autonomous_workforce

logger = logging.getLogger(__name__)

WORKSPACE_DIR = get_data_dir("personal_agent_workspace")
THREADS_DIR = os.path.join(WORKSPACE_DIR, "threads")
SETTINGS_FILE = os.path.join(WORKSPACE_DIR, "settings.json")
PID_FILE = os.path.join(WORKSPACE_DIR, "dashboard.pid")

os.makedirs(THREADS_DIR, exist_ok=True)

DEFAULT_PORT = 6796


def get_default_settings() -> Dict[str, Any]:
    return {
        "model_provider": "local_cpu_qwen",
        "model_name": "Qwen-3.5-9B-GGUF",
        "endpoint": "http://127.0.0.1:11434/v1",
        "temperature": 0.7,
        "spend_limit_usd": 100.0,
        "daily_briefing_time": "08:00",
        "auto_undo_sla": True,
        "port": DEFAULT_PORT
    }


def load_settings() -> Dict[str, Any]:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                base = get_default_settings()
                base.update(data)
                return base
        except Exception:
            pass
    settings = get_default_settings()
    save_settings(settings)
    return settings


def save_settings(settings: Dict[str, Any]) -> None:
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save settings: {e}")


def list_threads() -> List[Dict[str, Any]]:
    threads = []
    if not os.path.exists(THREADS_DIR):
        return threads

    for fname in os.listdir(THREADS_DIR):
        if fname.endswith(".json"):
            fpath = os.path.join(THREADS_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    threads.append(data)
            except Exception:
                continue

    threads.sort(key=lambda t: t.get("updated_at", 0), reverse=True)
    return threads


def get_thread(thread_id: str) -> Optional[Dict[str, Any]]:
    clean_id = os.path.basename(thread_id).replace(".json", "")
    fpath = os.path.join(THREADS_DIR, f"{clean_id}.json")
    if os.path.exists(fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_thread(thread_data: Dict[str, Any]) -> str:
    thread_id = thread_data.get("id") or f"thread_{int(time.time()*1000)}"
    thread_data["id"] = thread_id
    thread_data["updated_at"] = time.time()
    fpath = os.path.join(THREADS_DIR, f"{thread_id}.json")
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(thread_data, f, indent=2)
    return thread_id


# ==============================================================================
# HTML5 / Cyberpunk Dots-Style Dashboard Template
# ==============================================================================

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CIEAV — Sovereign Personal Agent Workspace (Dots Edition)</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🟣</text></svg>">
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: rgba(18, 24, 38, 0.85);
      --card-border: rgba(168, 85, 247, 0.25);
      --purple: #a855f7;
      --purple-hover: #c084fc;
      --cyan: #06b6d4;
      --emerald: #10b981;
      --amber: #f59e0b;
      --rose: #f43f5e;
      --text: #f1f5f9;
      --text-dim: #94a3b8;
      --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: radial-gradient(circle at 10% 20%, #17112b 0%, var(--bg) 80%);
      color: var(--text);
      font-family: var(--font);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
    }

    /* Top Nav */
    header {
      background: rgba(11, 15, 25, 0.95);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--card-border);
      padding: 0.85rem 1.75rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      text-decoration: none;
      color: inherit;
    }

    .pulse-dot {
      width: 14px;
      height: 14px;
      background: var(--purple);
      border-radius: 50%;
      box-shadow: 0 0 16px var(--purple);
      animation: pulse 2.5s infinite;
    }

    @keyframes pulse {
      0%, 100% { transform: scale(1); opacity: 1; filter: drop-shadow(0 0 12px #a855f7); }
      50% { transform: scale(1.15); opacity: 0.8; filter: drop-shadow(0 0 24px #c084fc); }
    }

    .brand h1 {
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      background: linear-gradient(135deg, #fff 0%, var(--purple-hover) 50%, var(--cyan) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .status-pills {
      display: flex;
      gap: 0.75rem;
      align-items: center;
    }

    .pill {
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .pill-green { color: var(--emerald); border-color: rgba(16, 185, 129, 0.3); }
    .pill-purple { color: var(--purple-hover); border-color: rgba(168, 85, 247, 0.3); }
    .pill-cyan { color: var(--cyan); border-color: rgba(6, 182, 212, 0.3); }

    /* Main Grid Layout */
    .app-container {
      display: grid;
      grid-template-columns: 320px 1fr 340px;
      flex: 1;
      height: calc(100vh - 65px);
      overflow: hidden;
    }

    /* Left Sidebar: Squads & History */
    .sidebar-left {
      background: rgba(15, 21, 34, 0.6);
      border-right: 1px solid var(--card-border);
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      overflow-y: auto;
    }

    .section-title {
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-dim);
      margin-bottom: 0.65rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .squad-card {
      background: var(--card-bg);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      padding: 0.75rem;
      cursor: pointer;
      transition: all 0.2s ease;
      margin-bottom: 0.5rem;
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .squad-card:hover, .squad-card.active {
      border-color: var(--purple);
      background: rgba(168, 85, 247, 0.12);
      transform: translateX(4px);
    }

    .squad-icon {
      font-size: 1.4rem;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.06);
    }

    .squad-meta h3 { font-size: 0.88rem; font-weight: 600; }
    .squad-meta p { font-size: 0.72rem; color: var(--text-dim); }

    .thread-item {
      padding: 0.65rem 0.85rem;
      border-radius: 8px;
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid transparent;
      cursor: pointer;
      font-size: 0.82rem;
      margin-bottom: 0.4rem;
      transition: all 0.2s ease;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .thread-item:hover, .thread-item.active {
      background: rgba(6, 182, 212, 0.12);
      border-color: var(--cyan);
      color: #fff;
    }

    /* Center Pane: Active Task & Conversation Workspace */
    .workspace-center {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: rgba(11, 15, 25, 0.4);
    }

    .thread-header {
      padding: 1.25rem 1.75rem;
      border-bottom: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(15, 21, 34, 0.4);
    }

    .thread-header h2 { font-size: 1.1rem; font-weight: 700; color: #fff; }
    .thread-header span { font-size: 0.78rem; color: var(--text-dim); }

    .messages-stream {
      flex: 1;
      padding: 1.75rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }

    .msg-bubble {
      max-width: 82%;
      padding: 1rem 1.25rem;
      border-radius: 12px;
      font-size: 0.92rem;
      line-height: 1.55;
      position: relative;
    }

    .msg-user {
      align-self: flex-end;
      background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(192, 132, 252, 0.15));
      border: 1px solid rgba(168, 85, 247, 0.4);
      color: #fff;
      border-bottom-right-radius: 2px;
    }

    .msg-agent {
      align-self: flex-start;
      background: var(--card-bg);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--text);
      border-bottom-left-radius: 2px;
    }

    .msg-header {
      display: flex;
      justify-content: space-between;
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--purple-hover);
      margin-bottom: 0.45rem;
    }

    .msg-receipt-badge {
      font-family: monospace;
      font-size: 0.7rem;
      color: var(--amber);
      background: rgba(245, 158, 11, 0.1);
      padding: 0.15rem 0.45rem;
      border-radius: 4px;
      border: 1px solid rgba(245, 158, 11, 0.25);
    }

    .composer-box {
      padding: 1.25rem 1.75rem;
      border-top: 1px solid var(--card-border);
      background: rgba(15, 21, 34, 0.7);
      display: flex;
      gap: 0.75rem;
    }

    .composer-input {
      flex: 1;
      background: rgba(0, 0, 0, 0.35);
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 10px;
      padding: 0.85rem 1.15rem;
      color: #fff;
      font-size: 0.95rem;
      font-family: inherit;
      outline: none;
      transition: border 0.2s;
    }

    .composer-input:focus { border-color: var(--purple); }

    .btn-send {
      background: linear-gradient(135deg, var(--purple) 0%, #9333ea 100%);
      color: #fff;
      border: none;
      border-radius: 10px;
      padding: 0 1.5rem;
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      transition: opacity 0.2s, transform 0.1s;
    }

    .btn-send:hover { opacity: 0.9; transform: scale(1.02); }

    /* Right Sidebar: Memory, 2PC Authority & Receipts */
    .sidebar-right {
      background: rgba(15, 21, 34, 0.6);
      border-left: 1px solid var(--card-border);
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      overflow-y: auto;
    }

    .receipt-row {
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      padding: 0.65rem 0.75rem;
      font-size: 0.75rem;
      margin-bottom: 0.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .receipt-id { font-family: monospace; color: var(--amber); }

    .btn-undo {
      background: rgba(244, 63, 94, 0.15);
      color: var(--rose);
      border: 1px solid rgba(244, 63, 94, 0.3);
      border-radius: 4px;
      padding: 0.25rem 0.5rem;
      font-size: 0.7rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-undo:hover {
      background: var(--rose);
      color: #fff;
    }

    .memory-item {
      font-size: 0.78rem;
      padding: 0.55rem 0.75rem;
      border-radius: 6px;
      background: rgba(255, 255, 255, 0.03);
      border-left: 3px solid var(--cyan);
      margin-bottom: 0.4rem;
    }
  </style>
</head>
<body>
  <header>
    <a href="/" class="brand">
      <div class="pulse-dot"></div>
      <h1>CIEAV DOTS PERSONAL AGENT</h1>
    </a>
    <div class="status-pills">
      <div class="pill pill-green">● 2PC SAFETY ACTIVE</div>
      <div class="pill pill-purple">PORT 6796</div>
      <div class="pill pill-cyan" id="model-pill">LOCAL QWEN-3.5-9B</div>
    </div>
  </header>

  <div class="app-container">
    <!-- Left Sidebar: Squads & Active Threads -->
    <aside class="sidebar-left">
      <div>
        <div class="section-title">
          <span>Assigned Squad / Agent</span>
        </div>
        <div class="squad-card active" onclick="selectSquad('Personal Agent', this)">
          <div class="squad-icon">🟣</div>
          <div class="squad-meta">
            <h3>Personal Agent</h3>
            <p>Universal Coordinator (All-Rounder)</p>
          </div>
        </div>
        <div class="squad-card" onclick="selectSquad('Researcher', this)">
          <div class="squad-icon">🔍</div>
          <div class="squad-meta">
            <h3>Researcher</h3>
            <p>Comparative Intel & Docs</p>
          </div>
        </div>
        <div class="squad-card" onclick="selectSquad('Product Team', this)">
          <div class="squad-icon">📋</div>
          <div class="squad-meta">
            <h3>Product Team</h3>
            <p>Roadmaps, Plans & Feedback</p>
          </div>
        </div>
        <div class="squad-card" onclick="selectSquad('Codex Engineer', this)">
          <div class="squad-icon">💻</div>
          <div class="squad-meta">
            <h3>Codex Engineer</h3>
            <p>AST Code Synthesis & Pytest</p>
          </div>
        </div>
        <div class="squad-card" onclick="selectSquad('Sentinel', this)">
          <div class="squad-icon">🛡️</div>
          <div class="squad-meta">
            <h3>Sentinel</h3>
            <p>Codebase Health & Auto-Heal</p>
          </div>
        </div>
      </div>

      <div>
        <div class="section-title">
          <span>Conversation Threads</span>
          <span style="cursor:pointer;" onclick="newThread()">+ New</span>
        </div>
        <div id="thread-list">
          <!-- Populated by JS -->
        </div>
      </div>
    </aside>

    <!-- Center Pane: Chat & Work Execution Area -->
    <main class="workspace-center">
      <div class="thread-header">
        <div>
          <h2 id="current-thread-title">General Task Workspace</h2>
          <span id="current-thread-meta">Active Squad: Personal Agent • 100% Local CPU</span>
        </div>
      </div>

      <div class="messages-stream" id="messages-container">
        <div class="msg-bubble msg-agent">
          <div class="msg-header">
            <span>🟣 CIEAV DOTS RUNTIME</span>
            <span class="msg-receipt-badge">2PC ARMED</span>
          </div>
          Welcome to your sovereign personal agent workspace! Assign any task directly from this browser dashboard or via CLI using <code>cieav work "your task"</code>.
        </div>
      </div>

      <div class="composer-box">
        <input type="text" id="task-input" class="composer-input" placeholder="Give the agent work... (e.g. 'Research three approaches and recommend one')" onkeydown="if(event.key==='Enter') submitTask()">
        <button class="btn-send" onclick="submitTask()">Dispatch Task</button>
      </div>
    </main>

    <!-- Right Sidebar: Memory Vault, Routines & 2PC Receipts -->
    <aside class="sidebar-right">
      <div>
        <div class="section-title">
          <span>Persistent Memory & Vault</span>
        </div>
        <div id="memory-list">
          <div class="memory-item">User prefers 100% local CPU execution without cloud APIs</div>
          <div class="memory-item">Daily morning briefing configured at 08:00 AM</div>
          <div class="memory-item">Residential ISP session preserved for quick-commerce</div>
        </div>
      </div>

      <div>
        <div class="section-title">
          <span>Ed25519 Receipts & 2PC Undo</span>
        </div>
        <div id="receipts-list">
          <div class="receipt-row">
            <div>
              <div class="receipt-id">rcpt_7f21a8bc</div>
              <div style="font-size:0.68rem; color:var(--text-dim);">AST Codebase Health Scan</div>
            </div>
            <button class="btn-undo" onclick="undoReceipt('rcpt_7f21a8bc')">/undo</button>
          </div>
        </div>
      </div>
    </aside>
  </div>

  <script>
    let currentSquad = "Personal Agent";
    let currentThreadId = null;

    async function loadWorkspace() {
      try {
        const res = await fetch("/api/threads");
        const threads = await res.json();
        renderThreadList(threads);

        const urlParams = new URLSearchParams(window.location.search);
        const requestedThread = urlParams.get("thread");
        if (requestedThread) {
          loadThread(requestedThread);
        } else if (threads.length > 0) {
          loadThread(threads[0].id);
        }
      } catch (e) {
        console.error("Failed to load threads", e);
      }
      loadReceipts();
      loadMemory();
    }

    function renderThreadList(threads) {
      const container = document.getElementById("thread-list");
      if (!threads || threads.length === 0) {
        container.innerHTML = '<div style="font-size:0.75rem; color:var(--text-dim); padding:0.5rem;">No active threads yet. Type a task below or run <code>cieav work</code>.</div>';
        return;
      }
      container.innerHTML = threads.map(t => `
        <div class="thread-item ${t.id === currentThreadId ? 'active' : ''}" onclick="loadThread('${t.id}')">
          ${t.title || 'Untitled Task'}
        </div>
      `).join('');
    }

    async function loadThread(threadId) {
      currentThreadId = threadId;
      try {
        const res = await fetch(`/api/threads/${threadId}`);
        const thread = await res.json();
        document.getElementById("current-thread-title").textContent = thread.title || "Task Thread";
        document.getElementById("current-thread-meta").textContent = `Assigned Squad: ${thread.squad || 'Personal Agent'} • ${new Date(thread.updated_at * 1000).toLocaleTimeString()}`;

        const msgContainer = document.getElementById("messages-container");
        msgContainer.innerHTML = (thread.messages || []).map(m => `
          <div class="msg-bubble ${m.role === 'user' ? 'msg-user' : 'msg-agent'}">
            <div class="msg-header">
              <span>${m.role === 'user' ? '👤 YOU' : '🟣 ' + (m.agent || 'CIEAV AGENT')}</span>
              ${m.receipt_id ? `<span class="msg-receipt-badge">${m.receipt_id}</span>` : ''}
            </div>
            <div>${m.content.replace(/\\n/g, '<br>')}</div>
          </div>
        `).join('');
        msgContainer.scrollTop = msgContainer.scrollHeight;
      } catch (e) {
        console.error("Error loading thread", e);
      }
    }

    function selectSquad(squadName, elem) {
      currentSquad = squadName;
      document.querySelectorAll(".squad-card").forEach(c => c.classList.remove("active"));
      elem.classList.add("active");
    }

    function newThread() {
      currentThreadId = null;
      document.getElementById("current-thread-title").textContent = "New Conversation";
      document.getElementById("messages-container").innerHTML = `
        <div class="msg-bubble msg-agent">
          <div class="msg-header"><span>🟣 CIEAV DOTS</span></div>
          What task would you like to assign to <strong>${currentSquad}</strong>?
        </div>
      `;
      document.getElementById("task-input").focus();
    }

    async function submitTask() {
      const input = document.getElementById("task-input");
      const task = input.value.trim();
      if (!task) return;

      input.value = "";
      const msgContainer = document.getElementById("messages-container");
      msgContainer.innerHTML += `
        <div class="msg-bubble msg-user">
          <div class="msg-header"><span>👤 YOU</span></div>
          ${task}
        </div>
        <div class="msg-bubble msg-agent" id="loading-msg">
          <div class="msg-header"><span>🟣 ${currentSquad}</span></div>
          <em>Thinking & executing under Two-Phase Commit safety floor...</em>
        </div>
      `;
      msgContainer.scrollTop = msgContainer.scrollHeight;

      try {
        const res = await fetch("/api/work", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            task: task,
            squad: currentSquad,
            thread_id: currentThreadId
          })
        });
        const data = await res.json();
        currentThreadId = data.thread_id;
        loadThread(currentThreadId);
        loadReceipts();
      } catch (e) {
        document.getElementById("loading-msg").innerHTML = `<span style="color:var(--rose);">Error: ${e.message}</span>`;
      }
    }

    async function loadReceipts() {
      try {
        const res = await fetch("/api/receipts");
        const list = await res.json();
        const container = document.getElementById("receipts-list");
        if (!list || list.length === 0) return;
        container.innerHTML = list.slice(0, 6).map(r => `
          <div class="receipt-row">
            <div>
              <div class="receipt-id">${r.receipt_id.substring(0, 14)}</div>
              <div style="font-size:0.68rem; color:var(--text-dim);">${r.tool_name || 'Action'}</div>
            </div>
            <button class="btn-undo" onclick="undoReceipt('${r.receipt_id}')">/undo</button>
          </div>
        `).join('');
      } catch (e) {}
    }

    async function loadMemory() {
      try {
        const res = await fetch("/api/memory");
        const items = await res.json();
        const container = document.getElementById("memory-list");
        if (!items || items.length === 0) return;
        container.innerHTML = items.slice(0, 5).map(m => `
          <div class="memory-item">${m.content || m.insight || m}</div>
        `).join('');
      } catch (e) {}
    }

    async function undoReceipt(receiptId) {
      if (confirm(`Trigger Two-Phase Commit rollback for receipt ${receiptId}?`)) {
        try {
          const res = await fetch(`/api/receipts/${receiptId}/undo`, { method: "POST" });
          const out = await res.json();
          alert(out.message || "Rollback committed successfully!");
          loadReceipts();
        } catch (e) {
          alert("Undo failed: " + e.message);
        }
      }
    }

    window.onload = loadWorkspace;
  </script>
</body>
</html>
"""


# ==============================================================================
# HTTP Request Handler for Dashboard & REST APIs
# ==============================================================================

class PersonalAgentHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Suppress noisy HTTP request logging
        pass

    def _send_json(self, status: int, data: Any):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_html(self, status: int, html_str: str):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_str.encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html", "/dashboard"):
            return self._send_html(200, DASHBOARD_HTML)

        if path == "/api/status":
            settings = load_settings()
            return self._send_json(200, {
                "status": "online",
                "version": "1.0.0-dots",
                "port": settings.get("port", DEFAULT_PORT),
                "model_provider": settings.get("model_provider"),
                "model_name": settings.get("model_name"),
                "spend_limit_usd": settings.get("spend_limit_usd"),
                "active_threads": len(list_threads())
            })

        if path == "/api/threads":
            return self._send_json(200, list_threads())

        if path.startswith("/api/threads/"):
            tid = path.split("/")[-1]
            thread = get_thread(tid)
            if thread:
                return self._send_json(200, thread)
            return self._send_json(404, {"error": "Thread not found"})

        if path == "/api/memory":
            recalled = memory_hive.recall("", top_k=6)
            return self._send_json(200, recalled)

        if path == "/api/receipts":
            rows = receipts.get_all_receipts()[-10:]
            rows.reverse()
            formatted = []
            for r in rows:
                formatted.append({
                    "receipt_id": r.get("id", ""),
                    "tool_name": r.get("tool", ""),
                    "outcome": r.get("outcome", ""),
                    "timestamp": r.get("timestamp", "")
                })
            return self._send_json(200, formatted)

        return self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            req_data = json.loads(body)
        except Exception:
            req_data = {}

        if path == "/api/work":
            from commit_layer.work_dispatcher import work_dispatcher
            task = req_data.get("task", "")
            squad = req_data.get("squad", "Personal Agent")
            tid = req_data.get("thread_id")
            res = work_dispatcher.dispatch(task=task, squad=squad, thread_id=tid, auto_open=False)
            return self._send_json(200, res)

        if path.startswith("/api/receipts/") and path.endswith("/undo"):
            parts = path.split("/")
            rcpt_id = parts[3]
            from commit_layer.cli import cmd_undo
            try:
                undo_res = receipts.compensate_receipt(rcpt_id)
                return self._send_json(200, {"status": "success", "message": f"Receipt {rcpt_id} successfully compensated via 2PC.", "result": undo_res})
            except Exception as e:
                return self._send_json(500, {"error": str(e)})

        if path == "/api/settings":
            current = load_settings()
            current.update(req_data)
            save_settings(current)
            return self._send_json(200, {"status": "saved", "settings": current})

        return self._send_json(404, {"error": "Endpoint not found"})


# ==============================================================================
# Dashboard Server Daemon Controller
# ==============================================================================

class PersonalAgentDashboardServer:
    """Manages the lifecycle of the http://127.0.0.1:6796 Dots-style dashboard."""

    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None

    def is_port_in_use(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", self.port)) == 0

    def start_background(self, auto_open: bool = False) -> Dict[str, Any]:
        """Start the dashboard server in a persistent background daemon thread."""
        if self.is_port_in_use():
            url = f"http://127.0.0.1:{self.port}"
            if auto_open:
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
            return {
                "status": "already_running",
                "port": self.port,
                "url": url,
                "message": f"CIEAV Personal Agent Dashboard is already active at {url}"
            }

        try:
            self.server = HTTPServer(("127.0.0.1", self.port), PersonalAgentHandler)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": f"Could not bind to port {self.port}: {e}"
            }

        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True, name="CIEAV-Dashboard-6796")
        self._thread.start()

        # Save PID
        try:
            with open(PID_FILE, "w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
        except Exception:
            pass

        url = f"http://127.0.0.1:{self.port}"
        if auto_open:
            try:
                webbrowser.open(url)
            except Exception:
                pass

        return {
            "status": "started",
            "port": self.port,
            "url": url,
            "message": f"CIEAV Personal Agent Dashboard successfully started at {url}"
        }

    def spawn_daemon_process(self, auto_open: bool = True) -> Dict[str, Any]:
        """Spawn independent background dashboard process on port 6796."""
        if self.is_port_in_use():
            url = f"http://127.0.0.1:{self.port}"
            if auto_open:
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
            return {
                "status": "already_running",
                "port": self.port,
                "url": url,
                "message": f"CIEAV Personal Agent Dashboard is already active at {url}"
            }

        repo_root = get_workspace_root()
        flags = 0x00000008 if os.name == "nt" else 0  # DETACHED_PROCESS on Windows
        proc = subprocess.Popen(
            [sys.executable, "-c", "from commit_layer.personal_agent_dashboard import run_server; run_server()"],
            cwd=repo_root,
            creationflags=flags,
            close_fds=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(1.0)

        url = f"http://127.0.0.1:{self.port}"
        if auto_open:
            try:
                webbrowser.open(url)
            except Exception:
                pass

        return {
            "status": "started",
            "pid": proc.pid,
            "port": self.port,
            "url": url,
            "message": f"CIEAV Personal Agent Dashboard successfully spawned in background at {url}"
        }

    def stop(self) -> Dict[str, Any]:
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, "r", encoding="utf-8") as f:
                    pid = int(f.read().strip())
                if os.name == "nt":
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                else:
                    import signal
                    os.kill(pid, signal.SIGTERM)
                if os.path.exists(PID_FILE):
                    os.remove(PID_FILE)
            except Exception:
                pass

        if self.server:
            try:
                self.server.shutdown()
                self.server.server_close()
            except Exception:
                pass
            self.server = None

        return {"status": "stopped", "message": "Dashboard server stopped cleanly."}

    def get_status(self) -> Dict[str, Any]:
        alive = self.is_port_in_use()
        settings = load_settings()
        threads = list_threads()
        return {
            "is_running": alive,
            "port": self.port,
            "url": f"http://127.0.0.1:{self.port}",
            "model_provider": settings.get("model_provider"),
            "model_name": settings.get("model_name"),
            "active_threads_count": len(threads),
            "threads": [t.get("title") for t in threads[:5]],
            "spend_cap_usd": settings.get("spend_limit_usd", 100.0)
        }


# Global singleton
dashboard_server = PersonalAgentDashboardServer(DEFAULT_PORT)


def run_server(port: int = DEFAULT_PORT):
    print(f"Starting CIEAV Personal Agent Dashboard on http://127.0.0.1:{port}...")
    server = HTTPServer(("127.0.0.1", port), PersonalAgentHandler)
    try:
        with open(PID_FILE, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        server.serve_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        server.server_close()
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except Exception:
                pass


if __name__ == "__main__":
    run_server()

