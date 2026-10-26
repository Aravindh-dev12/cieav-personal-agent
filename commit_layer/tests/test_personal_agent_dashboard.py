"""
Unit tests for CIEAV Personal Agent Web Dashboard & CLI Work Dispatcher.
"""
import os
import json
import time
import pytest
from commit_layer.personal_agent_dashboard import (
    load_settings, save_settings, list_threads, get_thread, save_thread,
    dashboard_server, DEFAULT_PORT
)
from commit_layer.work_dispatcher import work_dispatcher
from commit_layer import receipts


def test_settings_load_and_save():
    settings = load_settings()
    assert "model_provider" in settings
    assert settings.get("port") == DEFAULT_PORT

    original_cap = settings.get("spend_limit_usd", 100.0)
    settings["spend_limit_usd"] = 150.0
    save_settings(settings)

    reloaded = load_settings()
    assert reloaded["spend_limit_usd"] == 150.0

    # Restore
    settings["spend_limit_usd"] = original_cap
    save_settings(settings)


def test_thread_persistence_and_retrieval():
    tid = f"test_thread_{int(time.time()*1000)}"
    thread_data = {
        "id": tid,
        "title": "Unit Test Research Task",
        "squad": "Researcher",
        "created_at": time.time(),
        "updated_at": time.time(),
        "messages": [
            {"role": "user", "content": "Analyze system architecture", "timestamp": time.time()},
            {"role": "assistant", "agent": "Researcher", "content": "Analysis complete.", "timestamp": time.time()}
        ]
    }

    saved_id = save_thread(thread_data)
    assert saved_id == tid

    fetched = get_thread(tid)
    assert fetched is not None
    assert fetched["title"] == "Unit Test Research Task"
    assert len(fetched["messages"]) == 2

    all_threads = list_threads()
    assert any(t["id"] == tid for t in all_threads)


def test_work_dispatcher_researcher():
    res = work_dispatcher.dispatch(
        task="Research three approaches for zero-copy state transactions",
        agent="Researcher",
        auto_open=False
    )
    assert res["status"] == "success"
    assert res["agent"] == "Researcher"
    assert res.get("receipt_id") is not None
    assert "Approach A" in res["response"]
    assert "Approach C" in res["response"]

    # Verify receipt exists in SQLite ledger
    rcpt = receipts.get_receipt(res["receipt_id"])
    assert rcpt is not None
    assert rcpt["tool"] == "personal_agent_work"


def test_work_dispatcher_product_team():
    res = work_dispatcher.dispatch(
        task="Review rollout roadmap for personal agent companion",
        squad="Product Team",
        auto_open=False
    )
    assert res["status"] == "success"
    assert res["agent"] == "Product Team"
    assert res.get("receipt_id") is not None
    assert "Product Team Strategic Review" in res["response"]


def test_work_dispatcher_general_work():
    res = work_dispatcher.dispatch(
        task="Summarize current project status",
        auto_open=False
    )
    assert res["status"] == "success"
    assert res.get("receipt_id") is not None
    assert res.get("thread_id") is not None
    assert "http://127.0.0.1:6796" in res["dashboard_url"]


def test_dashboard_server_status():
    status = dashboard_server.get_status()
    assert "is_running" in status
    assert status["port"] == DEFAULT_PORT
    assert "active_threads_count" in status
    assert status["active_threads_count"] > 0
