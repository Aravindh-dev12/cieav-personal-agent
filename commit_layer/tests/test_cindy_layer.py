"""
Unit Tests for Cindy Architecture in CIEAV: Reviewer, Orca Teaming & Parity.
"""

from __future__ import annotations
import os
import tempfile
import pytest

from commit_layer.cindy_layer import (
    cindy_reviewer,
    orca_orchestrator,
    input_handoff,
    Severity,
    Finding,
    ReviewReport,
)
from commit_layer.tools.base import TOOL_REGISTRY


def test_reviewer_clean_workspace():
    """Verify review on the commit_layer directory produces structured report."""
    report = cindy_reviewer.review_workspace(target_path="commit_layer")
    assert report.report_id.startswith("rev_")
    assert isinstance(report.findings, list)
    assert isinstance(report.inspected_files, list)
    assert report.elapsed_sec >= 0.0

    card = cindy_reviewer.render_review_card(report)
    assert "CINDY INDEPENDENT REVIEWER" in card
    assert "Two-Phase Commit Floor" in card


def test_reviewer_detects_syntax_and_secrets(tmp_path):
    """Verify Reviewer flags P1 for broken syntax and P0 for raw hardcoded secrets."""
    bad_code_path = tmp_path / "broken_service.py"
    bad_code_path.write_text(
        'api_key = "abcdef1234567890abcdef1234567890"\n'
        'def broken_function(\n'
        '    print("missing closing paren"\n',
        encoding="utf-8"
    )

    report = cindy_reviewer.review_workspace(target_path=str(tmp_path))
    assert report.passed is False

    severities = [f.severity for f in report.findings]
    assert Severity.P1_HIGH in severities  # Syntax error
    assert Severity.P0_CRITICAL in severities  # Hardcoded API key

    p0_finding = next(f for f in report.findings if f.severity == Severity.P0_CRITICAL)
    assert p0_finding.category == "security"
    assert "Never commit raw secrets" in p0_finding.recommendation


def test_orca_multi_agent_team():
    """Verify Lead/Worker orchestration completes and certifies with 2PC receipt."""
    res = orca_orchestrator.execute_team_mission(
        directive="Scaffold rate limiter with unit tests",
        lead_model="minimaxai/minimax-m3.1-flash"
    )

    assert res["status"] == "success"
    assert res["team_id"].startswith("orca_team_")
    assert bool(res["receipt_id"])
    assert len(res["workers"]) == 2

    builder = next(w for w in res["workers"] if w["label"] == "builder")
    reviewer = next(w for w in res["workers"] if w["label"] == "reviewer")

    assert builder["status"] == "completed"
    assert reviewer["status"] == "completed"
    assert builder["receipt_id"] == res["receipt_id"]


def test_input_handoff_lifecycle():
    """Verify credentials in Input Handoff are volatile and purged immediately."""
    token_id = "test_token_123"
    input_handoff._transient_store[token_id] = "SuperSecretPassword123!"

    # First retrieval succeeds
    val = input_handoff.retrieve_and_purge(token_id)
    assert val == "SuperSecretPassword123!"

    # Subsequent retrieval returns None (purged)
    assert input_handoff.retrieve_and_purge(token_id) is None


def test_agent_user_parity_tools():
    """Verify Agent-User parity: Agent has tools for review, scheduling, and undo."""
    assert "cindy_review" in TOOL_REGISTRY
    assert "cindy_scheduler" in TOOL_REGISTRY
    assert "cindy_undo" in TOOL_REGISTRY

    review_tool = TOOL_REGISTRY["cindy_review"]
    res = review_tool.execute({"target": "commit_layer"})
    assert res["status"] == "success"
    assert "findings_count" in res

    sched_tool = TOOL_REGISTRY["cindy_scheduler"]
    res_sched = sched_tool.execute({"action": "status"})
    assert res_sched["status"] == "success"
    assert "active_routines" in res_sched
