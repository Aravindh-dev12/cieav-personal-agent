"""Tests for CIEAV Meeting & Technical Defense Knowledge Base QA Engine."""
import pytest
from commit_layer.ask import CieavKnowledgeQA, cieav_qa


def test_knowledge_base_loaded():
    qa = CieavKnowledgeQA()
    assert len(qa.entries) >= 10
    entry_ids = [e["id"] for e in qa.entries]
    assert "2pc_architecture" in entry_ids
    assert "post_training_reward_hacking" in entry_ids
    assert "huggingface_model" in entry_ids


def test_answer_reward_hacking():
    res = cieav_qa.answer("How do you prevent models from cheating the reward function?")
    assert res["status"] == "success"
    entry = res["entry"]
    assert entry["id"] == "post_training_reward_hacking"
    assert "RLVR" in entry["short_answer"] or "RLVR" in entry["full_answer"]
    assert "-1.0" in entry["full_answer"]


def test_answer_rollback_2pc():
    res = cieav_qa.answer("Explain how undo and rollback work in 2PC")
    assert res["status"] == "success"
    entry = res["entry"]
    assert entry["id"] == "2pc_architecture"
    assert "observe" in entry["full_answer"]
    assert "inverse" in entry["full_answer"]


def test_answer_huggingface_model():
    res = cieav_qa.answer("What is inside the model uploaded to Hugging Face?")
    assert res["status"] == "success"
    entry = res["entry"]
    assert entry["id"] == "huggingface_model"
    assert "safetensors" in entry["full_answer"].lower()


def test_answer_empty_query():
    res = cieav_qa.answer("")
    assert res["status"] == "empty"
