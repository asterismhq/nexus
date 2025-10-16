"""Unit tests for the dependency injection system."""

from dev.mocks.mock_mlx_client import MockMLXClient
from dev.mocks.mock_ollama_client import MockOllamaClient
from dev.mocks.mock_vllm_client import MockVLLMClient
from nexus.config import NexusSettings
from nexus.dependencies import get_app_settings, get_llm_client


def test_get_app_settings_returns_singleton() -> None:
    """get_app_settings should return cached singleton instance."""
    settings1 = get_app_settings()
    settings2 = get_app_settings()

    assert settings1 is settings2
    assert settings1.app_name == "nexus"


def test_get_llm_client_returns_mock_ollama_when_enabled(monkeypatch) -> None:
    """get_llm_client should return Ollama mock when use_mock_ollama is True."""
    monkeypatch.setenv("NEXUS_LLM_BACKEND", "ollama")
    monkeypatch.setenv("NEXUS_USE_MOCK_OLLAMA", "true")
    app_settings = NexusSettings()

    client = get_llm_client(settings=app_settings)

    assert isinstance(client, MockOllamaClient)


def test_get_llm_client_returns_mock_mlx_when_enabled(monkeypatch) -> None:
    """get_llm_client should return MLX mock when use_mock_mlx is True."""
    monkeypatch.setenv("NEXUS_LLM_BACKEND", "mlx")
    monkeypatch.setenv("NEXUS_USE_MOCK_MLX", "true")
    monkeypatch.setenv("NEXUS_MLX_HOST", "http://localhost:8080")
    app_settings = NexusSettings()

    client = get_llm_client(settings=app_settings)

    assert isinstance(client, MockMLXClient)


def test_get_llm_client_returns_mock_vllm_when_enabled(monkeypatch) -> None:
    """get_llm_client should return vLLM mock when use_mock_vllm is True."""
    monkeypatch.setenv("NEXUS_LLM_BACKEND", "vllm")
    monkeypatch.setenv("NEXUS_USE_MOCK_VLLM", "true")
    app_settings = NexusSettings()

    client = get_llm_client(settings=app_settings)

    assert isinstance(client, MockVLLMClient)


def test_get_llm_client_falls_back_to_ollama_on_unknown_backend(monkeypatch) -> None:
    """Unknown backends should fall back to Ollama mock when use_mock_ollama is True."""
    monkeypatch.setenv("NEXUS_LLM_BACKEND", "does-not-exist")
    monkeypatch.setenv("NEXUS_USE_MOCK_OLLAMA", "true")
    app_settings = NexusSettings()

    client = get_llm_client(settings=app_settings)

    assert isinstance(client, MockOllamaClient)
