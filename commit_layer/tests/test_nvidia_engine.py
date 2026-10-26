"""
Unit Tests for NVIDIA Nemotron 3.5 Bolt Inference Engine & CIEAV Integration.
"""

from __future__ import annotations
import json
from unittest.mock import MagicMock, patch
import pytest

from commit_layer.nvidia_engine import NvidiaNemotronEngine, DEFAULT_ENDPOINT, DEFAULT_MODEL
from commit_layer.work_dispatcher import WorkDispatcher


@pytest.fixture
def test_engine():
    """Create isolated engine instance with mock key."""
    engine = NvidiaNemotronEngine(api_key="nvapi-testkey-1234567890abcdef")
    return engine


def test_engine_initialization():
    engine = NvidiaNemotronEngine()
    assert engine.model == DEFAULT_MODEL
    assert engine.endpoint == DEFAULT_ENDPOINT
    assert engine.endpoint == "https://integrate.api.nvidia.com/v1/chat/completions"
    assert engine.model == "nvidia/nemotron-3.5-bolt-e4b"


def test_key_management():
    engine = NvidiaNemotronEngine(api_key="nvapi-secret-key-12345")
    assert engine.is_available() is True
    assert engine.get_api_key() == "nvapi-secret-key-12345"

    st = engine.get_status()
    assert st["available"] is True
    assert st["model"] == DEFAULT_MODEL
    assert "nvapi-s" in st["api_key_masked"]
    assert st["thinking_enabled"] is True


def test_chat_completion_mock(test_engine):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "chatcmpl-test-123",
        "model": "nvidia/nemotron-3.5-bolt-e4b",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "reasoning_content": "Comparing 9.11 and 9.8: 9.8 is 9.80, which is strictly greater than 9.11.",
                    "content": "9.8 is larger than 9.11."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 30, "total_tokens": 50}
    }

    with patch("requests.post", return_value=mock_response) as mock_post:
        messages = [{"role": "user", "content": "Which number is larger, 9.11 or 9.8?"}]
        res = test_engine.chat_completion(messages=messages)

        assert res["status"] == "success"
        assert res["content"] == "9.8 is larger than 9.11."
        assert "9.8 is 9.80" in res["thinking"]
        assert res["model"] == "nvidia/nemotron-3.5-bolt-e4b"

        # Verify payload structure matches NVIDIA API specification
        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs["json"]
        headers = call_kwargs["headers"]

        assert headers["Authorization"] == "Bearer nvapi-testkey-1234567890abcdef"
        assert payload["model"] == "nvidia/nemotron-3.5-bolt-e4b"
        assert payload["parallel_tool_calls"] is True
        assert payload["chat_template_kwargs"]["enable_thinking"] is True
        assert payload["temperature"] == 1.0
        assert payload["top_p"] == 0.95
        assert payload["seed"] == 42


def test_embedded_think_tag_parsing(test_engine):
    """Test extracting reasoning if returned inside <think> tags."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "chatcmpl-tag-test",
        "model": "nvidia/nemotron-3.5-bolt-e4b",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "<think>Step 1: Parse operands. Step 2: Conclude 9.8 > 9.11.</think>9.8 is larger than 9.11."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {}
    }

    with patch("requests.post", return_value=mock_response):
        res = test_engine.chat_completion(messages=[{"role": "user", "content": "test"}])
        assert res["status"] == "success"
        assert "Step 1: Parse operands" in res["thinking"]
        assert res["content"] == "9.8 is larger than 9.11."


def test_streaming_chat_mock(test_engine):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.iter_lines.return_value = [
        b'data: {"choices": [{"delta": {"reasoning_content": "Thinking step 1... "}}]}',
        b'data: {"choices": [{"delta": {"reasoning_content": "Thinking step 2... "}}]}',
        b'data: {"choices": [{"delta": {"content": "Final "}}]}',
        b'data: {"choices": [{"delta": {"content": "Answer."}}]}',
        b'data: [DONE]'
    ]

    with patch("requests.post", return_value=mock_response):
        messages = [{"role": "user", "content": "hello"}]
        chunks = list(test_engine.stream_chat(messages=messages))

        thinking_chunks = [c["chunk"] for c in chunks if c.get("type") == "thinking"]
        content_chunks = [c["chunk"] for c in chunks if c.get("type") == "content"]
        done_chunks = [c for c in chunks if c.get("type") == "done"]

        assert len(thinking_chunks) == 2
        assert len(content_chunks) == 2
        assert len(done_chunks) == 1
        assert done_chunks[0]["total_thinking"] == "Thinking step 1... Thinking step 2... "
        assert done_chunks[0]["total_content"] == "Final Answer."


def test_no_api_key_graceful_handling():
    engine = NvidiaNemotronEngine(api_key="")
    # With no key, should fail cleanly with informative error
    res = engine.chat_completion(messages=[{"role": "user", "content": "test"}])
    assert res["status"] == "error"
    assert "NVIDIA_API_KEY not configured" in res["error"]


def test_generate_agent_reasoning(test_engine):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "chatcmpl-agent-test",
        "model": "nvidia/nemotron-3.5-bolt-e4b",
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "reasoning_content": "Analyzing security implications under 2PC...",
                    "content": "### Security Assessment\nAll transactions are bounded by Ed25519 hash-chain receipts."
                }
            }
        ]
    }

    with patch("requests.post", return_value=mock_response):
        res = test_engine.generate_agent_reasoning(agent_role="Security Sentinel", task="Audit auth gateway")
        assert res["status"] == "success"
        assert res["agent"] == "Security Sentinel"
        assert "Analyzing security implications" in res["thinking"]
        assert "Security Assessment" in res["content"]


def test_work_dispatcher_with_nvidia(test_engine):
    dispatcher = WorkDispatcher()

    # Mock nvidia_engine within work_dispatcher
    with patch("commit_layer.work_dispatcher.nvidia_engine.is_available", return_value=True):
        with patch("commit_layer.work_dispatcher.nvidia_engine.generate_agent_reasoning") as mock_gen:
            mock_gen.return_value = {
                "status": "success",
                "content": "Synthesized Nemotron response for task.",
                "thinking": "Decomposed task into atomic phases.",
                "elapsed_sec": 0.42
            }
            res = dispatcher.dispatch(task="Research quantum encryption", agent="Researcher", auto_open=False)
            assert res["status"] == "success"
            assert bool(res["receipt_id"])
            assert "Synthesized Nemotron response" in res["response"]
            assert "Nemotron 3.5 Bolt Chain-of-Thought" in res["response"]
