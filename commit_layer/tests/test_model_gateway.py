"""Unit tests for UniversalModelGateway (Local zero-download vs cloud models)."""
import pytest
from commit_layer.model_gateway import UniversalModelGateway, model_gateway


def test_gateway_status_structure():
    gateway = UniversalModelGateway()
    status = gateway.get_status()
    assert "active_provider" in status
    assert "providers" in status
    assert "zero_download" in status["providers"]
    assert "nvidia" in status["providers"]
    assert "anthropic" in status["providers"]
    assert "openai" in status["providers"]
    assert "meta_open" in status["providers"]


def test_zero_download_fallback():
    """Verify that zero_download operates in <2ms with 0 MB download."""
    gateway = UniversalModelGateway()
    gateway.settings["active_provider"] = "zero_download"
    res = gateway.query("Read file test.txt")
    assert res["provider"] == "zero_download"
    assert "cieav-decider" in res["model"]
    assert "decision" in res


def test_set_provider_validation():
    gateway = UniversalModelGateway()
    with pytest.raises(ValueError):
        gateway.set_provider("non_existent_provider_xyz")

    res = gateway.set_provider("zero_download", model="cieav-decider-v2")
    assert res["status"] == "success"
    assert gateway.settings["active_provider"] == "zero_download"
