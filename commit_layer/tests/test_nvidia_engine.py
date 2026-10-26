"""
Unit Tests for NVIDIA Inference Engine: MiniMax-M3.1-Flash & Nemotron-3.5-Bolt.
"""

from __future__ import annotations
import json
from unittest.mock import MagicMock, patch
import pytest

from commit_layer.nvidia_engine import (
    NvidiaInferenceEngine,
    NvidiaNemotronEngine,
    DEFAULT_ENDPOINT,
    DEFAULT_MODEL,
    MODEL_MINIMAX_FLASH,
    MODEL_NEMOTRON_BOLT,
)
from commit_layer.work_dispatcher import WorkDispatcher


@pytest.fixture
def test_engine():
    """Create isolated engine instance with mock key and MiniMax-M3.1-Flash."""
    engine = NvidiaInferenceEngine(api_key="nvapi-testkey-1234567890abcdef", model=MODEL_MINIMAX_FLASH)
    return engine


def test_engine_initialization():
    engine = NvidiaInferenceEngine(model=MODEL_MINIMAX_FLASH)
    assert engine.model == MODEL_MINIMAX_FLASH
    assert engine.endpoint == DEFAULT_ENDPOINT
    assert engine.endpoint == "https://integrate.api.nvidia.com/v1/chat/completions"
    assert engine.model == "minimaxai/minimax-m3.1-flash"


def test_key_management():
    engine = NvidiaInferenceEngine(api_key="nvapi-secret-key-12345", model=MODEL_MINIMAX_FLASH)
    assert engine.is_available() is True
    assert engine.get_api_key() == "nvapi-secret-key-12345"

    st = engine.get_status()
    assert st["available"] is True
    assert st["model"] == MODEL_MINIMAX_FLASH
    assert "nvapi-s" in st["api_key_masked"]
    assert st["is_minimax"] is True
    assert st["capabilities"]["multimodal_vision"] is True
    assert st["capabilities"]["max_tokens"] == 16384


def test_model_switching(test_engine):
    # Switch to Nemotron
    resolved = test_engine.set_model("nemotron", persist=False)
    assert resolved == MODEL_NEMOTRON_BOLT
    assert test_engine.model == MODEL_NEMOTRON_BOLT
    st = test_engine.get_status()
    assert st["is_minimax"] is False
    assert st["capabilities"]["cot_thinking"] is True

    # Switch back to MiniMax
    resolved2 = test_engine.set_model("minimax", persist=False)
    assert resolved2 == MODEL_MINIMAX_FLASH
    assert test_engine.model == MODEL_MINIMAX_FLASH


def test_minimax_multimodal_vision(test_engine):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "chatcmpl-minimax-vis-123",
        "model": "minimaxai/minimax-m3.1-flash",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "The image displays an architectural blueprint diagram."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {"prompt_tokens": 120, "completion_tokens": 15, "total_tokens": 135}
    }

    with patch("requests.post", return_value=mock_response) as mock_post:
        img_url = "https://assets.ngc.nvidia.com/products/api-catalog/phi-3-5-vision/example1b.jpg"
        res = test_engine.analyze_multimodal(
            prompt="What is in this image?",
            image_source=img_url
        )

        assert res["status"] == "success"
        assert "architectural blueprint" in res["content"]

        # Validate request payload matches MiniMax specifications
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs["json"]
        headers = call_kwargs["headers"]

        assert headers["Authorization"] == "Bearer nvapi-testkey-1234567890abcdef"
        assert payload["model"] == "minimaxai/minimax-m3.1-flash"
        assert payload["seed"] == 0
        assert payload["temperature"] == 1.0
        assert payload["top_p"] == 0.95

        # Check multimodal content structure
        msg_content = payload["messages"][0]["content"]
        assert isinstance(msg_content, list)
        assert msg_content[0]["type"] == "text"
        assert msg_content[0]["text"] == "What is in this image?"
        assert msg_content[1]["type"] == "image_url"
        assert msg_content[1]["image_url"]["url"] == img_url


def test_minimax_agentic_workflow(test_engine):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "chatcmpl-minimax-code-456",
        "model": "minimaxai/minimax-m3.1-flash",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "```python\ndef synthesize_agentic_pipeline():\n    return True\n```"
                }
            }
        ]
    }

    with patch("requests.post", return_value=mock_response) as mock_post:
        res = test_engine.generate_agentic_workflow(
            workflow_type="coding",
            directive="Scaffold an autonomous file audit routine"
        )

        assert res["status"] == "success"
        assert res["workflow_type"] == "coding"
        assert "synthesize_agentic_pipeline" in res["content"]

        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs["json"]
        assert payload["model"] == "minimaxai/minimax-m3.1-flash"
        assert payload["max_tokens"] == 8192


def test_nemotron_cot_chat_completion():
    nemotron_engine = NvidiaInferenceEngine(
        api_key="nvapi-testkey-nemotron",
        model=MODEL_NEMOTRON_BOLT
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "chatcmpl-nemotron-123",
        "model": "nvidia/nemotron-3.5-bolt-e4b",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "reasoning_content": "Comparing 9.11 and 9.8: 9.8 is strictly greater than 9.11.",
                    "content": "9.8 is larger than 9.11."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 30, "total_tokens": 50}
    }

    with patch("requests.post", return_value=mock_response) as mock_post:
        messages = [{"role": "user", "content": "Which number is larger, 9.11 or 9.8?"}]
        res = nemotron_engine.chat_completion(messages=messages, max_tokens=1024)

        assert res["status"] == "success"
        assert res["content"] == "9.8 is larger than 9.11."
        assert "strictly greater" in res["thinking"]

        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs["json"]
        assert payload["chat_template_kwargs"]["enable_thinking"] is True
        assert payload["parallel_tool_calls"] is True


def test_streaming_chat_mock(test_engine):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = [
        b'data: {"choices": [{"delta": {"content": "Autonomous "}}]}',
        b'data: {"choices": [{"delta": {"content": "Workforce "}}]}',
        b'data: {"choices": [{"delta": {"content": "Ready."}}]}',
        b'data: [DONE]'
    ]

    with patch("requests.post", return_value=mock_response):
        messages = [{"role": "user", "content": "status check"}]
        chunks = list(test_engine.stream_chat(messages=messages))

        content_chunks = [c["chunk"] for c in chunks if c.get("type") == "content"]
        done_chunks = [c for c in chunks if c.get("type") == "done"]

        assert len(content_chunks) == 3
        assert len(done_chunks) == 1
        assert done_chunks[0]["total_content"] == "Autonomous Workforce Ready."


def test_work_dispatcher_with_minimax(test_engine):
    dispatcher = WorkDispatcher()

    with patch("commit_layer.work_dispatcher.nvidia_engine.is_available", return_value=True):
        with patch("commit_layer.work_dispatcher.nvidia_engine.generate_agent_reasoning") as mock_gen:
            mock_gen.return_value = {
                "status": "success",
                "content": "MiniMax-M3.1-Flash synthesized workflow: Decomposed architecture into 3 microservices.",
                "thinking": "",
                "elapsed_sec": 0.28
            }
            res = dispatcher.dispatch(task="Design microservices", agent="Codex Engineer", auto_open=False)
            assert res["status"] == "success"
            assert bool(res["receipt_id"])
            assert "MiniMax-M3.1-Flash" in res["response"]
