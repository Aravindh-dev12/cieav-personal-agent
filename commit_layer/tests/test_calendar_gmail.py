"""Tests for Autonomous Calendar and Gmail Agent Tools under Two-Phase Commit."""
from __future__ import annotations
import pytest
from commit_layer.personal_agent import CieavPersonalAgent
from commit_layer.tools import calendar_agent
from commit_layer.tools import gmail_agent


def test_calendar_get_events():
    events = calendar_agent.get_calendar_events()
    assert isinstance(events, list)
    assert len(events) >= 1
    assert "title" in events[0]
    assert "time" in events[0]


def test_calendar_render_dossier():
    events = calendar_agent.get_calendar_events()
    card = calendar_agent.render_calendar_dossier(events)
    assert "CIEAV Sovereign Calendar Dossier" in card
    assert "Two-Phase Commit" in card


def test_personal_agent_calendar_check():
    agent = CieavPersonalAgent()
    res = agent.execute("check my calendar for today")
    assert res["status"] == "success"
    assert res["domain"] == "calendar"
    assert "CIEAV Sovereign Calendar Dossier" in res["message"]


def test_personal_agent_calendar_schedule():
    agent = CieavPersonalAgent()
    res = agent.execute("schedule meeting with Engineering Team at 03:00 PM")
    assert res["status"] == "success"
    assert res["domain"] == "calendar_schedule"
    assert "Meeting Scheduled under Two-Phase Commit" in res["message"]


def test_personal_agent_gmail_check():
    agent = CieavPersonalAgent()
    res = agent.execute("check my gmail inbox")
    assert res["status"] == "success"
    assert "GMAIL" in res["message"].upper()


def test_personal_agent_gmail_compose_intent():
    intent = gmail_agent.detect_gmail_intent("send an email to team@cieav.dev saying release is live")
    assert intent is not None
    assert intent.get("intent") == "compose_and_send"
    assert intent.get("to") == "team@cieav.dev"
