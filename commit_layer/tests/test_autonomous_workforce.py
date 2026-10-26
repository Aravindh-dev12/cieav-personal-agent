"""
Unit tests for CIEAV Autonomous Personal Agentic Workforce (100% Local CPU • 2PC Governance).
"""
import os
import tempfile
import pytest
from commit_layer.autonomous_workforce import (
    CodebaseSentinel, AutonomousFileEngineer, WorkforceDaemon,
    AutonomousWorkforceOrchestrator, autonomous_workforce
)
from commit_layer import gateway, receipts


def test_sentinel_scan_workspace():
    sentinel = CodebaseSentinel()
    scan = sentinel.scan_workspace()
    assert scan["total_files"] > 0
    assert scan["py_files_count"] > 0
    assert scan["total_lines"] > 0
    assert "health_score" in scan
    assert scan["elapsed_sec"] < 15.0


def test_engineer_inspect_and_update_governed():
    engineer = AutonomousFileEngineer()

    # Create temporary file to test file mutation with snapshot and 2PC
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
        f.write("# Initial test file\nx = 10\n")
        temp_path = f.name

    try:
        # 1. Inspect
        insp = engineer.inspect_file(temp_path)
        assert insp["status"] == "success"
        assert insp["ast_valid"] is True
        assert insp["lines_count"] == 2

        # 2. Update with AST validation under 2PC
        new_code = "# Updated by workforce\nx = 20\ndef foo():\n    return x * 2\n"
        up_res = engineer.update_file_governed(temp_path, new_code, reason="Unit test update")
        assert up_res["status"] == "committed"
        assert up_res["bytes_written"] > 0
        assert up_res.get("receipt_id") is not None

        # Verify on disk
        with open(temp_path, "r", encoding="utf-8") as f:
            disk_content = f.read()
        assert "def foo():" in disk_content

        # 3. Test Rejection of Invalid Python Code
        bad_code = "def broken(\n"
        bad_res = engineer.update_file_governed(temp_path, bad_code, reason="Should fail AST")
        assert bad_res["status"] == "rejected"
        assert "AST Safety Validation Failed" in bad_res["error"]

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_engineer_patch_file():
    engineer = AutonomousFileEngineer()
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as f:
        f.write("DEBUG_MODE = False\nDATABASE_URL = 'sqlite:///test.db'\n")
        temp_path = f.name

    try:
        res = engineer.patch_file(temp_path, "DEBUG_MODE = False", "DEBUG_MODE = True", reason="Enable debug")
        assert res["status"] == "committed"
        with open(temp_path, "r", encoding="utf-8") as f:
            assert "DEBUG_MODE = True" in f.read()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_workforce_daemon_lifecycle():
    daemon = WorkforceDaemon()
    assert not daemon.is_running

    # Start
    start_res = daemon.start(interval_sec=10, auto_heal=False)
    assert start_res["status"] == "started"
    assert daemon.is_running is True

    # Status
    st = daemon.status()
    assert st["is_running"] is True

    # Stop
    stop_res = daemon.stop()
    assert stop_res["status"] == "stopped"
    assert daemon.is_running is False


def test_personal_agent_workforce_routing():
    from commit_layer.personal_agent import cieav_personal_agent
    res = cieav_personal_agent.execute("autonomously check and update files")
    assert res["status"] == "success"
    assert res["domain"] == "workforce"
    assert "CIEAV AUTONOMOUS WORKFORCE" in res["message"]
