"""Unit tests for the dependency container."""

from dev.mocks.mock_mlx_client import MockMLXClient
from dev.mocks.mock_ollama_client import MockOllamaClient
from stella_connector.config import AppSettings
from stella_connector.container import DependencyContainer


def test_dependency_container_exposes_settings_defaults() -> None:
    """Container should expose default application settings."""
    container = DependencyContainer()

    assert container.settings.app_name == "stella-connector"
    assert container.settings.debug is False
    assert container.settings.llm_backend == "ollama"
    assert container.settings.use_mock_ollama is False
    assert container.settings.use_mock_mlx is False


def test_dependency_container_accepts_custom_settings() -> None:
    """Container should accept injected settings instances."""
    custom_settings = AppSettings(app_name="custom-app", debug=True)

    container = DependencyContainer(app_settings=custom_settings)

    assert container.settings.app_name == "custom-app"
    assert container.settings.debug is True


def test_provide_llm_client_returns_mock_ollama_when_enabled() -> None:
    """Container should return the Ollama mock when requested."""

    app_settings = AppSettings(use_mock_ollama=True)
    container = DependencyContainer(app_settings=app_settings)

    client = container.provide_llm_client()

    assert isinstance(client, MockOllamaClient)


def test_provide_llm_client_returns_mock_mlx_when_enabled() -> None:
    """Container should return the MLX mock when requested."""

    app_settings = AppSettings(llm_backend="mlx", use_mock_mlx=True)
    container = DependencyContainer(app_settings=app_settings)

    client = container.provide_llm_client()

    assert isinstance(client, MockMLXClient)


def test_provide_llm_client_falls_back_to_ollama_on_unknown_backend() -> None:
    """Unknown backends should fall back to the Ollama mock when enabled."""

    app_settings = AppSettings(llm_backend="does-not-exist", use_mock_ollama=True)
    container = DependencyContainer(app_settings=app_settings)

    client = container.provide_llm_client()

    assert isinstance(client, MockOllamaClient)
