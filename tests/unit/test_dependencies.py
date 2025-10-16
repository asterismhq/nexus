"""Unit tests for the dependency injection system."""

from dev.mocks.mock_mlx_client import MockMLXClient
from dev.mocks.mock_ollama_client import MockOllamaClient
from nexus.config import AppSettings
from nexus.dependencies import get_app_settings, get_llm_client


def test_get_app_settings_returns_singleton() -> None:
    """get_app_settings should return cached singleton instance."""
    settings1 = get_app_settings()
    settings2 = get_app_settings()

    assert settings1 is settings2
    assert settings1.app_name == "nexus"


def test_get_llm_client_returns_mock_ollama_when_enabled() -> None:
    """get_llm_client should return Ollama mock when use_mock_ollama is True."""
    app_settings = AppSettings(use_mock_ollama=True)

    client = get_llm_client(settings=app_settings)

    assert isinstance(client, MockOllamaClient)


def test_get_llm_client_returns_mock_mlx_when_enabled() -> None:
    """get_llm_client should return MLX mock when use_mock_mlx is True."""
    app_settings = AppSettings(llm_backend="mlx", use_mock_mlx=True)

    client = get_llm_client(settings=app_settings)

    assert isinstance(client, MockMLXClient)


def test_get_llm_client_falls_back_to_ollama_on_unknown_backend() -> None:
    """Unknown backends should fall back to Ollama mock when use_mock_ollama is True."""
    app_settings = AppSettings(llm_backend="does-not-exist", use_mock_ollama=True)

    client = get_llm_client(settings=app_settings)

    assert isinstance(client, MockOllamaClient)
