"""
CIEAV Universal Model Gateway & Agent Connector Hub.
===================================================
Provides seamless switching between:
1. Local Model Options:
   - zero_download_cpu : 0 MB download! In-process deterministic AST consequence engine & fast heuristic.
   - unsloth_lora      : Lightweight post-trained LoRA adapter (<50MB) via Unsloth.
   - local_gguf        : In-process Qwen-3.5-9B GGUF on CPU (if downloaded).
   - ollama / vllm     : Local host endpoints (http://localhost:11434).

2. Cloud Model Options:
   - nvidia            : NVIDIA NIM (Nemotron 3.5 Bolt CoT, MiniMax-M3.1-Flash MoE).
   - anthropic         : Claude 3.5 Sonnet, Claude 3 Haiku.
   - openai            : ChatGPT (GPT-4o, GPT-4o-mini, o1).
   - meta_open         : Meta Llama-3.3, Meta Muse via Groq or OpenRouter.

3. External Agent Support (Dots, Meta Muse, Claude Code, AutoGPT):
   - External agents connect via standard OpenAI-compatible completions (/v1/chat/completions).
   - Every tool call or state mutation is governed by CIEAV's Two-Phase Commit (2PC) safety floor
     with atomic filesystem snapshots and Ed25519-signed receipts.
"""

from __future__ import annotations
import os
import sys
import json
import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("cieav.model_gateway")


class UniversalModelGateway:
    """Central routing hub for Local, Cloud, and Agentic models."""

    SETTINGS_PATH = Path("personal_agent_workspace/settings.json")

    PROVIDERS = {
        "zero_download": {
            "name": "Local Sovereign (0 MB Download)",
            "type": "local",
            "desc": "In-process CPU AST consequence engine + templates. 0 MB download, sub-2ms latency.",
            "free": True
        },
        "nvidia": {
            "name": "NVIDIA Free Endpoints",
            "type": "cloud",
            "desc": "Nemotron 3.5 Bolt (CoT Thinking) & MiniMax-M3.1-Flash (MoE 16k, Vision).",
            "free": True
        },
        "anthropic": {
            "name": "Anthropic Claude",
            "type": "cloud",
            "desc": "Claude 3.5 Sonnet & Claude 3 Haiku.",
            "free": False
        },
        "openai": {
            "name": "OpenAI ChatGPT",
            "type": "cloud",
            "desc": "GPT-4o, GPT-4o-mini, and o1 reasoning models.",
            "free": False
        },
        "meta_open": {
            "name": "Meta Llama / Muse / Groq",
            "type": "cloud",
            "desc": "Meta Llama-3.3-70B, Muse, or Mistral via Groq/OpenRouter.",
            "free": True
        },
        "local_gguf": {
            "name": "Local Qwen-3.5-9B (GGUF)",
            "type": "local",
            "desc": "In-process quantized GGUF on local CPU (if downloaded).",
            "free": True
        },
        "ollama": {
            "name": "Local Ollama / vLLM",
            "type": "local",
            "desc": "Local BYOM endpoint (http://127.0.0.1:11434).",
            "free": True
        }
    }

    def __init__(self):
        self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        self.settings: Dict[str, Any] = {
            "active_provider": "zero_download",
            "active_model": "cieav-decider-v2",
            "openai_api_key": os.environ.get("OPENAI_API_KEY", ""),
            "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "nvidia_api_key": os.environ.get("NVIDIA_API_KEY", ""),
            "groq_api_key": os.environ.get("GROQ_API_KEY", ""),
            "openrouter_api_key": os.environ.get("OPENROUTER_API_KEY", ""),
        }
        if self.SETTINGS_PATH.exists():
            try:
                data = json.loads(self.SETTINGS_PATH.read_text(encoding="utf-8"))
                if "model_provider" in data:
                    self.settings["active_provider"] = data["model_provider"]
                if "model_name" in data:
                    self.settings["active_model"] = data["model_name"]
                if "nvidia_api_key" in data and data["nvidia_api_key"]:
                    self.settings["nvidia_api_key"] = data["nvidia_api_key"]
            except Exception as e:
                logger.warning(f"Failed to read settings: {e}")

        # Check if NVIDIA is ready to use
        if self.settings["nvidia_api_key"] and self.settings["active_provider"] in ("nvidia", "zero_download"):
            self.settings["active_provider"] = "nvidia"

        return self.settings

    def save_settings(self):
        self.SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.SETTINGS_PATH.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")

    def get_status(self) -> Dict[str, Any]:
        """Return operational status of all model providers."""
        return {
            "active_provider": self.settings.get("active_provider", "zero_download"),
            "active_model": self.settings.get("active_model", "cieav-decider-v2"),
            "providers": self.PROVIDERS,
            "has_nvidia_key": bool(self.settings.get("nvidia_api_key")),
            "has_openai_key": bool(self.settings.get("openai_api_key")),
            "has_anthropic_key": bool(self.settings.get("anthropic_api_key")),
            "has_groq_key": bool(self.settings.get("groq_api_key")),
        }

    def set_provider(self, provider: str, model: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Set the active model provider and persist configuration."""
        if provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(self.PROVIDERS.keys())}")

        self.settings["active_provider"] = provider
        if model:
            self.settings["active_model"] = model
        if api_key:
            if provider == "nvidia":
                self.settings["nvidia_api_key"] = api_key
                os.environ["NVIDIA_API_KEY"] = api_key
            elif provider == "openai":
                self.settings["openai_api_key"] = api_key
                os.environ["OPENAI_API_KEY"] = api_key
            elif provider == "anthropic":
                self.settings["anthropic_api_key"] = api_key
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif provider == "meta_open":
                self.settings["groq_api_key"] = api_key
                os.environ["GROQ_API_KEY"] = api_key

        self.save_settings()
        return {"status": "success", "provider": provider, "model": self.settings["active_model"]}

    def query(self, prompt: str, system_prompt: str = "", agent_role: str = "Personal Agent") -> Dict[str, Any]:
        """
        Unified dispatch: attempts active provider, with automatic zero-download CPU fallback.
        """
        provider = self.settings.get("active_provider", "zero_download")

        # 1. NVIDIA Free NIM (Nemotron / MiniMax)
        if provider == "nvidia":
            from commit_layer.nvidia_engine import nvidia_engine
            if nvidia_engine.is_available():
                try:
                    res = nvidia_engine.generate_agent_reasoning(agent_role=agent_role, task=prompt)
                    if res.get("status") == "success":
                        return {
                            "provider": "nvidia",
                            "model": nvidia_engine.model,
                            "content": res.get("content", ""),
                            "thinking": res.get("thinking", ""),
                            "elapsed_sec": res.get("elapsed_sec", 0.0)
                        }
                except Exception as e:
                    logger.warning(f"NVIDIA call failed: {e}. Falling back to zero_download.")

        # 2. OpenAI ChatGPT (if configured)
        if provider == "openai" and self.settings.get("openai_api_key"):
            res = self._call_openai_compatible(
                base_url="https://api.openai.com/v1",
                api_key=self.settings["openai_api_key"],
                model=self.settings.get("active_model", "gpt-4o-mini"),
                prompt=prompt,
                system_prompt=system_prompt
            )
            if res.get("status") == "success":
                return res

        # 3. Anthropic Claude (if configured)
        if provider == "anthropic" and self.settings.get("anthropic_api_key"):
            res = self._call_anthropic(
                api_key=self.settings["anthropic_api_key"],
                model=self.settings.get("active_model", "claude-3-5-sonnet-20241022"),
                prompt=prompt,
                system_prompt=system_prompt
            )
            if res.get("status") == "success":
                return res

        # 4. Meta Llama / Groq (if configured)
        if provider == "meta_open" and (self.settings.get("groq_api_key") or self.settings.get("openrouter_api_key")):
            key = self.settings.get("groq_api_key") or self.settings.get("openrouter_api_key")
            base_url = "https://api.groq.com/openai/v1" if self.settings.get("groq_api_key") else "https://openrouter.ai/api/v1"
            res = self._call_openai_compatible(
                base_url=base_url,
                api_key=key,
                model=self.settings.get("active_model", "llama-3.3-70b-versatile"),
                prompt=prompt,
                system_prompt=system_prompt
            )
            if res.get("status") == "success":
                return res

        # 5. Local GGUF (if downloaded & available)
        if provider == "local_gguf":
            try:
                from commit_layer.hybrid_brain import hybrid_brain
                if hybrid_brain.engine.is_available:
                    res = hybrid_brain.process_query(prompt, use_live_model=True)
                    return {
                        "provider": "local_gguf",
                        "model": "qwen3.5-9b",
                        "content": res.get("message", ""),
                    }
            except Exception:
                pass

        # 6. Default Guaranteed Zero-Download In-Process Fallback (0 MB disk, <2ms)
        from commit_layer.decision_model import local_decision_model
        dec = local_decision_model.inspect_decision(prompt)
        return {
            "provider": "zero_download",
            "model": "cieav-decider-v2",
            "content": f"[CIEAV Sovereign Personal Agent • Zero-Download CPU]\n"
                       f"Action evaluated with 100% on-device privacy under Two-Phase Commit.\n"
                       f"Decision: {dec.get('top_choice')} (Score: {dec.get('consequence_score', 0):.2f})",
            "decision": dec
        }

    def _call_openai_compatible(self, base_url: str, api_key: str, model: str, prompt: str, system_prompt: str) -> Dict[str, Any]:
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps({"model": model, "messages": messages, "temperature": 0.7}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                return {"status": "success", "provider": "openai_compatible", "model": model, "content": content}
        except Exception as e:
            logger.warning(f"OpenAI compatible call failed: {e}")
            return {"status": "error", "error": str(e)}

    def _call_anthropic(self, api_key: str, model: str, prompt: str, system_prompt: str) -> Dict[str, Any]:
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        body: Dict[str, Any] = {
            "model": model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system_prompt:
            body["system"] = system_prompt

        payload = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = "".join([c.get("text", "") for c in data.get("content", [])])
                return {"status": "success", "provider": "anthropic", "model": model, "content": content}
        except Exception as e:
            logger.warning(f"Anthropic call failed: {e}")
            return {"status": "error", "error": str(e)}


# Global singleton
model_gateway = UniversalModelGateway()
