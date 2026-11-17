"""
Unit tests for CIEAV PyBot Symbolic Engine (Pure-Python Zero-Weight Sovereign Reasoning).
Inspired by Hugging Face's PyBot (huggingface/pybot).
"""

import pytest
from commit_layer.pybot_engine import (
    PyBotEngine,
    PyBotUnderstandingLayer,
    PyBotMemoryLayer,
    PyBotKnowledgeLayer,
    PyBotComposeLayer,
    pybot_engine
)
from commit_layer.model_gateway import UniversalModelGateway


def test_pybot_understanding_intents():
    layer = PyBotUnderstandingLayer()
    assert layer.parse_intent("audit security vulnerabilities and secrets") == "security_audit"
    assert layer.parse_intent("please patch the config and update file") == "file_mutation"
    assert layer.parse_intent("run cindy code review on this PR") == "code_review"
    assert layer.parse_intent("rollback the last transaction and undo") == "rollback"
    assert layer.parse_intent("is it safe or is there danger of reward hack") == "risk_query"
    assert layer.parse_intent("orchestrate a swarm with orca and codex") == "swarm_orchestration"
    assert layer.parse_intent("explain the architecture of CIEAV") == "knowledge_query"


def test_pybot_risk_assessment_critical():
    layer = PyBotUnderstandingLayer()
    risk, reasons = layer.assess_symbolic_risk("sudo rm -rf / --no-preserve-root")
    assert risk == "CRITICAL"
    assert len(reasons) > 0

    risk2, _ = layer.assess_symbolic_risk("inspect and leak .ssh/id_rsa keys")
    assert risk2 == "CRITICAL"

    risk3, _ = layer.assess_symbolic_risk("cat .env and print API_KEY")
    assert risk3 == "HIGH"

    risk4, reasons4 = layer.assess_symbolic_risk("list all python files in tests directory")
    assert risk4 == "LOW"
    assert "No dangerous shell or credential patterns" in reasons4[0]


def test_pybot_memory_layer():
    memory = PyBotMemoryLayer(max_history=5)
    assert memory.get_last_turn() is None

    from commit_layer.pybot_engine import DialogueTurn
    turn1 = DialogueTurn("hello", "general", "LOW", "ok", "response1")
    memory.record(turn1)
    assert memory.get_last_turn().user_prompt == "hello"

    for i in range(10):
        memory.record(DialogueTurn(f"prompt {i}", "general", "LOW", "ok", f"resp {i}"))
    assert len(memory.history) == 5
    assert memory.get_last_turn().user_prompt == "prompt 9"

    memory.clear()
    assert len(memory.history) == 0


def test_pybot_knowledge_layer():
    knowledge = PyBotKnowledgeLayer()
    fact_cieav = knowledge.query("what is cieav?")
    assert fact_cieav is not None
    assert "Two-Phase Commit" in fact_cieav

    fact_pybot = knowledge.query("tell me about the pybot pure python engine")
    assert fact_pybot is not None
    assert "huggingface/pybot" in fact_pybot

    fact_rh = knowledge.query("how does it stop reward hacking?")
    assert fact_rh is not None
    assert "RLVR" in fact_rh


def test_pybot_compose_proposal():
    composer = PyBotComposeLayer()
    crit_prop = composer.compose_2pc_proposal("rm -rf /", "file_mutation", "CRITICAL", ["Destructive root deletion"])
    assert crit_prop["status"] == "prepared"
    assert crit_prop["risk_assessment"]["permit_required"] is True
    assert crit_prop["risk_assessment"]["requires_human_consensus"] is True
    assert crit_prop["execution_plan"]["action"] == "hold_for_signature"

    low_prop = composer.compose_2pc_proposal("git status", "general_query", "LOW", ["Safe read"])
    assert low_prop["risk_assessment"]["permit_required"] is False
    assert low_prop["execution_plan"]["action"] == "execute_governed_task"


def test_pybot_engine_e2e():
    engine = PyBotEngine()
    res = engine.process("Run security audit on git diff and check for .env leaks")
    assert res["status"] == "success"
    assert res["provider"] == "pybot_symbolic"
    assert res["pure_python"] is True
    assert res["zero_weights"] is True
    assert res["risk_level"] == "HIGH"
    assert res["proposal"]["risk_assessment"]["permit_required"] is True
    assert res["elapsed_ms"] < 50.0  # sub-50ms execution guaranteed


def test_model_gateway_pybot_integration():
    gateway = UniversalModelGateway()
    gateway.set_provider("pybot_symbolic")
    assert gateway.settings["active_provider"] == "pybot_symbolic"

    res = gateway.query("explain the two phase commit safety floor")
    assert res["status"] == "success"
    assert res["provider"] == "pybot_symbolic"
    assert "Two-Phase Commit" in res["content"]
    assert res["risk_level"] == "LOW"

    # Reset
    gateway.set_provider("zero_download")
