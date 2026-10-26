"""
NVIDIA Inference Engine for CIEAV: MiniMax-M3.1-Flash & Nemotron-3.5-Bolt.
==========================================================================
Integrates NVIDIA's API catalog endpoints for high-throughput multimodal
agentic workflows, coding, computer use, cybersecurity, and reasoning under Two-Phase Commit governance:

Supported Models:
  1. minimaxai/minimax-m3.1-flash (Default for Agentic Workflows):
     - Native multimodal mixture-of-experts (MoE)
     - Specialized in: Coding, Agentic Workflows, Computer Use, and Cybersecurity
     - Massive context: 16,384 output tokens
     - Multimodal vision support (text + image_url / base64 screenshots)
  2. nvidia/nemotron-3.5-bolt-e4b:
     - Native chain-of-thought (CoT) reasoning
     - Deep decomposition & comparative synthesis
"""

from __future__ import annotations
import os
import re
import json
import time
import base64
import logging
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

import requests

logger = logging.getLogger(__name__)

DEFAULT_ENDPOINT = "https://integrate.api.nvidia.com/v1/chat/completions"

MODEL_MINIMAX_FLASH = "minimaxai/minimax-m3.1-flash"
MODEL_NEMOTRON_BOLT = "nvidia/nemotron-3.5-bolt-e4b"
DEFAULT_MODEL = MODEL_MINIMAX_FLASH

MODEL_ALIASES = {
    "minimax": MODEL_MINIMAX_FLASH,
    "minimax-m3.1-flash": MODEL_MINIMAX_FLASH,
    "minimaxai/minimax-m3.1-flash": MODEL_MINIMAX_FLASH,
    "nemotron": MODEL_NEMOTRON_BOLT,
    "nemotron-3.5-bolt": MODEL_NEMOTRON_BOLT,
    "nvidia/nemotron-3.5-bolt-e4b": MODEL_NEMOTRON_BOLT,
}

WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "..", "personal_agent_workspace")
SETTINGS_FILE = os.path.join(WORKSPACE_DIR, "settings.json")


class NvidiaInferenceEngine:
    """Multi-model client for NVIDIA's build API endpoints."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        endpoint: str = DEFAULT_ENDPOINT,
    ):
        self._explicit_key = api_key
        self.endpoint = endpoint or DEFAULT_ENDPOINT
        if model is not None:
            clean = model.strip().lower()
            self.model = MODEL_ALIASES.get(clean) or MODEL_ALIASES.get(clean.split("/")[-1]) or model.strip()
        else:
            self.model = self._load_saved_model(DEFAULT_MODEL)

    def _load_saved_model(self, fallback: str) -> str:
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    m = settings.get("nvidia_model") or settings.get("model_name")
                    if m in MODEL_ALIASES.values():
                        return m
            except Exception:
                pass
        return fallback

    # ──────────────────────────────────────────────────────────────────────────
    # Model Selection & Status
    # ──────────────────────────────────────────────────────────────────────────

    def set_model(self, model_name: str, persist: bool = True) -> str:
        """Switch active model between MiniMax-M3.1-Flash and Nemotron."""
        clean = model_name.strip().lower()
        resolved = MODEL_ALIASES.get(clean) or MODEL_ALIASES.get(clean.split("/")[-1])
        if not resolved:
            resolved = model_name.strip()

        self.model = resolved

        if persist:
            try:
                os.makedirs(WORKSPACE_DIR, exist_ok=True)
                current = {}
                if os.path.exists(SETTINGS_FILE):
                    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                        current = json.load(f)
                current["nvidia_model"] = resolved
                current["model_name"] = resolved
                current["model_provider"] = "nvidia"
                with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                    json.dump(current, f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to persist model setting: {e}")

        return resolved

    def get_api_key(self) -> Optional[str]:
        """
        Retrieve API key in order of precedence:
        1. Explicitly initialized key
        2. Environment variable NVIDIA_API_KEY
        3. personal_agent_workspace/settings.json ('nvidia_api_key')
        4. .env in project root
        """
        if self._explicit_key:
            return self._explicit_key

        env_key = os.environ.get("NVIDIA_API_KEY", "").strip()
        if env_key:
            return env_key

        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    key = settings.get("nvidia_api_key", "").strip()
                    if key:
                        return key
            except Exception:
                pass

        return None

    def set_api_key(self, api_key: str, persist_to_settings: bool = True) -> None:
        """Set active API key and optionally save to settings.json."""
        cleaned = api_key.strip()
        self._explicit_key = cleaned
        os.environ["NVIDIA_API_KEY"] = cleaned

        if persist_to_settings:
            try:
                os.makedirs(WORKSPACE_DIR, exist_ok=True)
                current = {}
                if os.path.exists(SETTINGS_FILE):
                    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                        current = json.load(f)
                current["nvidia_api_key"] = cleaned
                current["nvidia_model"] = self.model
                current["model_provider"] = "nvidia"
                current["model_name"] = self.model
                with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                    json.dump(current, f, indent=2)
            except Exception as e:
                logger.warning(f"Failed to persist NVIDIA key to {SETTINGS_FILE}: {e}")

    def is_available(self) -> bool:
        """Returns True if a valid API key is configured."""
        key = self.get_api_key()
        return bool(key and len(key) > 5)

    def get_status(self) -> Dict[str, Any]:
        """Return diagnostic status of the NVIDIA inference engine."""
        key = self.get_api_key()
        masked = f"{key[:7]}...{key[-4:]}" if key and len(key) > 12 else ("Configured" if key else "Not set")
        is_minimax = "minimax" in self.model
        return {
            "available": self.is_available(),
            "model": self.model,
            "endpoint": self.endpoint,
            "api_key_masked": masked,
            "supported_models": [
                MODEL_MINIMAX_FLASH,
                MODEL_NEMOTRON_BOLT
            ],
            "is_minimax": is_minimax,
            "capabilities": {
                "agentic_workflows": True,
                "coding_moe": is_minimax,
                "multimodal_vision": is_minimax,
                "computer_use": True,
                "cybersecurity": True,
                "cot_thinking": not is_minimax,
                "max_tokens": 16384 if is_minimax else 2048,
            }
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Chat & Multimodal Completions
    # ──────────────────────────────────────────────────────────────────────────

    def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 1.0,
        top_p: float = 0.95,
        max_tokens: Optional[int] = None,
        seed: Optional[int] = None,
        enable_thinking: bool = True,
        tools: Optional[List[Dict[str, Any]]] = None,
        timeout: int = 60,
    ) -> Dict[str, Any]:
        """
        Execute completion against MiniMax-M3.1-Flash or Nemotron-3.5-Bolt.
        Supports multimodal content:
          content: [{"type": "text", "text": "..."}, {"type": "image_url", "image_url": {"url": "..."}}]
        """
        api_key = self.get_api_key()
        if not api_key:
            return {
                "status": "error",
                "error": "NVIDIA_API_KEY not configured. Set via 'cieav nvidia key <key>' or .env",
                "content": "",
                "thinking": "",
                "model": self.model
            }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        is_minimax = "minimax" in self.model

        # Token & seed defaults customized per model spec
        if max_tokens is None:
            max_tokens = 16384 if is_minimax else 1024
        if seed is None:
            seed = 0 if is_minimax else 42

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "seed": seed,
            "stream": False,
        }

        # Model-specific parameters
        if not is_minimax:
            payload["parallel_tool_calls"] = True
            payload["chat_template_kwargs"] = {"enable_thinking": enable_thinking}

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        t_start = time.time()
        try:
            resp = requests.post(self.endpoint, headers=headers, json=payload, timeout=timeout)
            elapsed = time.time() - t_start

            if resp.status_code != 200:
                err_msg = f"NVIDIA API Error [{resp.status_code}]: {resp.text}"
                logger.error(err_msg)
                return {
                    "status": "error",
                    "error": err_msg,
                    "status_code": resp.status_code,
                    "elapsed_sec": round(elapsed, 3),
                    "content": "",
                    "thinking": "",
                    "model": self.model
                }

            data = resp.json()
            choice = data.get("choices", [{}])[0]
            msg = choice.get("message", {})

            # Extract reasoning/thinking tokens
            thinking = msg.get("reasoning_content") or ""
            raw_content = msg.get("content") or ""

            # If content is a list of blocks, extract text
            if isinstance(raw_content, list):
                text_parts = [b.get("text", "") for b in raw_content if isinstance(b, dict) and b.get("type") == "text"]
                raw_content = "".join(text_parts)

            # If thinking is embedded in <think> tags within content
            if not thinking and "<think>" in str(raw_content):
                think_match = re.search(r'<think>(.*?)</think>', raw_content, flags=re.DOTALL)
                if think_match:
                    thinking = think_match.group(1).strip()
                    raw_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()

            tool_calls = msg.get("tool_calls", [])

            return {
                "status": "success",
                "model": data.get("model", self.model),
                "content": raw_content,
                "thinking": thinking,
                "tool_calls": tool_calls,
                "finish_reason": choice.get("finish_reason", "stop"),
                "usage": data.get("usage", {}),
                "elapsed_sec": round(elapsed, 3)
            }

        except requests.exceptions.RequestException as e:
            elapsed = time.time() - t_start
            logger.error(f"NVIDIA API request exception: {e}")
            return {
                "status": "error",
                "error": f"Network or connection error connecting to NVIDIA API: {e}",
                "elapsed_sec": round(elapsed, 3),
                "content": "",
                "thinking": "",
                "model": self.model
            }

    # ──────────────────────────────────────────────────────────────────────────
    # Streaming Generator
    # ──────────────────────────────────────────────────────────────────────────

    def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 1.0,
        top_p: float = 0.95,
        max_tokens: Optional[int] = None,
        seed: Optional[int] = None,
        enable_thinking: bool = True,
        tools: Optional[List[Dict[str, Any]]] = None,
        timeout: int = 60,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Stream response tokens from NVIDIA endpoint.
        """
        api_key = self.get_api_key()
        if not api_key:
            yield {
                "type": "error",
                "error": "NVIDIA_API_KEY not configured. Set via 'cieav nvidia key <key>' or .env"
            }
            return

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        }

        is_minimax = "minimax" in self.model
        if max_tokens is None:
            max_tokens = 16384 if is_minimax else 1024
        if seed is None:
            seed = 0 if is_minimax else 42

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "seed": seed,
            "stream": True,
        }
        if not is_minimax:
            payload["parallel_tool_calls"] = True
            payload["chat_template_kwargs"] = {"enable_thinking": enable_thinking}

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        total_thinking: List[str] = []
        total_content: List[str] = []

        try:
            resp = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                stream=True,
                timeout=timeout
            )
            if resp.status_code != 200:
                yield {
                    "type": "error",
                    "error": f"NVIDIA API Stream Error [{resp.status_code}]: {resp.text}"
                }
                return

            for line in resp.iter_lines():
                if not line:
                    continue
                line_str = line.decode("utf-8").strip()
                if not line_str.startswith("data:"):
                    continue

                raw_data = line_str[5:].strip()
                if raw_data == "[DONE]":
                    break

                try:
                    chunk_json = json.loads(raw_data)
                    delta = chunk_json.get("choices", [{}])[0].get("delta", {})

                    r_chunk = delta.get("reasoning_content")
                    if r_chunk:
                        total_thinking.append(r_chunk)
                        yield {"type": "thinking", "chunk": r_chunk}

                    c_chunk = delta.get("content")
                    if c_chunk:
                        total_content.append(c_chunk)
                        yield {"type": "content", "chunk": c_chunk}

                    t_chunk = delta.get("tool_calls")
                    if t_chunk:
                        yield {"type": "tool_call", "delta": t_chunk}

                except Exception:
                    continue

            yield {
                "type": "done",
                "total_thinking": "".join(total_thinking),
                "total_content": "".join(total_content)
            }

        except Exception as e:
            yield {
                "type": "error",
                "error": f"Stream error: {e}"
            }

    # ──────────────────────────────────────────────────────────────────────────
    # Multimodal Vision Analysis (Screenshots, UI, Photos)
    # ──────────────────────────────────────────────────────────────────────────

    def analyze_multimodal(
        self,
        prompt: str,
        image_source: str,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        Analyzes an image using MiniMax-M3.1-Flash multimodal vision.
        image_source can be:
          1. Web URL (http:// or https://)
          2. Local file path (e.g., screenshots/desktop.png) -> encoded as data URI
        """
        image_url = image_source.strip()

        # Handle local file paths by converting to base64 data URI
        if not (image_url.startswith("http://") or image_url.startswith("https://") or image_url.startswith("data:")):
            if os.path.exists(image_url):
                ext = os.path.splitext(image_url)[1].lower().replace(".", "") or "png"
                mime = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"
                try:
                    with open(image_url, "rb") as img_f:
                        b64 = base64.b64encode(img_f.read()).decode("utf-8")
                        image_url = f"data:{mime};base64,{b64}"
                except Exception as e:
                    return {"status": "error", "error": f"Failed to encode image file {image_source}: {e}"}
            else:
                return {"status": "error", "error": f"Image file not found: {image_source}"}

        # Build multimodal payload matching MiniMax specification
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]

        # Use MiniMax-M3.1-Flash for multimodal tasks
        saved_model = self.model
        try:
            self.model = MODEL_MINIMAX_FLASH
            return self.chat_completion(messages=messages, max_tokens=max_tokens, seed=0)
        finally:
            self.model = saved_model

    # ──────────────────────────────────────────────────────────────────────────
    # Domain Agentic Workflow Synthesis (Coding, Computer Use, Cybersecurity)
    # ──────────────────────────────────────────────────────────────────────────

    def generate_agentic_workflow(
        self,
        workflow_type: str,
        directive: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes specialized Agentic Workflows using MiniMax-M3.1-Flash Mixture-of-Experts:
          - 'coding': Production code synthesis, AST validation, pytest suites
          - 'agentic_workflow': Multi-agent task decomposition, DAG planning
          - 'computer_use': Desktop GUI interaction, browser automation, app control
          - 'cybersecurity': Threat modeling, sandbox auditing, Ed25519 hash-chain receipts
        """
        domain_prompts = {
            "coding": (
                "You are the Lead Software Architect & Codex Engineer in CIEAV.\n"
                "Synthesize robust, production-grade, type-annotated code with 100% test coverage.\n"
                "Validate against Two-Phase Commit principles and AST syntax rules."
            ),
            "agentic_workflow": (
                "You are the Autonomous Workforce Coordinator in CIEAV.\n"
                "Decompose complex goals into verifiable atomic steps with clear risk assessments and receipts.\n"
                "Identify pre-conditions, tool assignments, and compensation rollback inverses."
            ),
            "computer_use": (
                "You are the Sovereign Computer Use & Desktop Operator in CIEAV.\n"
                "Formulate actionable UI automation actions (window focus, app launch, click coordinates, keystrokes).\n"
                "Ensure failsafes and rollback boundaries are strictly enforced."
            ),
            "cybersecurity": (
                "You are the Security Sentinel & Audit Guard in CIEAV.\n"
                "Audit the directive for privilege escalations, unsafe file deletions, injection attacks, and cognitive fatigue.\n"
                "Verify Ed25519 Merkle signatures and sandbox confinement."
            )
        }

        system_instruction = domain_prompts.get(workflow_type.lower(), domain_prompts["agentic_workflow"])

        user_content = f"Directive: {directive}"
        if context:
            user_content += f"\n\nContext & Workspace State:\n{context}"

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ]

        # Execute with MiniMax-M3.1-Flash MoE with 16k token capability
        res = self.chat_completion(
            messages=messages,
            max_tokens=8192 if "minimax" in self.model else 2048,
            temperature=1.0,
            top_p=0.95
        )

        if res.get("status") == "success":
            return {
                "status": "success",
                "workflow_type": workflow_type,
                "model": self.model,
                "content": res.get("content", ""),
                "thinking": res.get("thinking", ""),
                "elapsed_sec": res.get("elapsed_sec", 0),
                "usage": res.get("usage", {})
            }
        return res

    def generate_agent_reasoning(
        self,
        agent_role: str,
        task: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Persona reasoning for CIEAV squads (Researcher, Product, Codex, Sentinel).
        Maps to MiniMax-M3.1-Flash or Nemotron.
        """
        role_lower = agent_role.lower()
        if "coder" in role_lower or "engineer" in role_lower:
            return self.generate_agentic_workflow("coding", task, context)
        elif "sentinel" in role_lower or "security" in role_lower:
            return self.generate_agentic_workflow("cybersecurity", task, context)
        elif "gui" in role_lower or "computer" in role_lower:
            return self.generate_agentic_workflow("computer_use", task, context)
        else:
            return self.generate_agentic_workflow("agentic_workflow", task, context)

    # ──────────────────────────────────────────────────────────────────────────
    # Live Validation Tests
    # ──────────────────────────────────────────────────────────────────────────

    def test_connection(self) -> Dict[str, Any]:
        """
        Runs validation prompt against current active model:
        - MiniMax-M3.1-Flash: Tests agentic workflow synthesis or multimodal prompt
        - Nemotron: Tests canonical 9.11 vs 9.8 reasoning prompt
        """
        if "minimax" in self.model:
            # Canonical MiniMax multimodal / agentic test
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image?"},
                        {"type": "image_url", "image_url": {"url": "https://assets.ngc.nvidia.com/products/api-catalog/phi-3-5-vision/example1b.jpg"}}
                    ]
                }
            ]
            return self.chat_completion(
                messages=messages,
                temperature=1.0,
                top_p=0.95,
                max_tokens=1024,
                seed=0
            )
        else:
            # Canonical Nemotron prompt
            messages = [
                {"role": "user", "content": "Which number is larger, 9.11 or 9.8?"}
            ]
            return self.chat_completion(
                messages=messages,
                temperature=1.0,
                top_p=0.95,
                max_tokens=1024,
                seed=42,
                enable_thinking=True
            )


# Alias class for backwards compatibility
NvidiaNemotronEngine = NvidiaInferenceEngine

# Global singleton instance
nvidia_engine = NvidiaInferenceEngine()
