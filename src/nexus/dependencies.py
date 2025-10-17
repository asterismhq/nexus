"""FastAPI dependency providers for the nexus service."""

from __future__ import annotations

import importlib
import logging
from functools import lru_cache
from typing import Callable, Type

from fastapi import Depends

from .clients.mlx_client import MLXClient
from .clients.ollama_client import OllamaClient
from .config import MLXSettings, NexusSettings, OllamaSettings
from .protocols.llm_client_protocol import LLMClientProtocol

LOGGER = logging.getLogger(__name__)

# Factory type definitions
ClientFactory = Callable[[NexusSettings], LLMClientProtocol]
MockFactory = Callable[[NexusSettings], LLMClientProtocol]


def _create_ollama_client(_settings: NexusSettings) -> OllamaClient:
    """Create an Ollama client instance."""
    return OllamaClient(OllamaSettings())


def _create_mlx_client(_settings: NexusSettings) -> LLMClientProtocol:
    """Create an MLX client instance."""
    return MLXClient(MLXSettings())


def _create_mock_ollama_client(_settings: NexusSettings) -> LLMClientProtocol:
    """Create a mock Ollama client instance."""
    mock_class = _import_mock_class("dev.mocks.mock_ollama_client.MockOllamaClient")
    return mock_class(OllamaSettings())


def _create_mock_mlx_client(_settings: NexusSettings) -> LLMClientProtocol:
    """Create a mock MLX client instance."""
    mock_class = _import_mock_class("dev.mocks.mock_mlx_client.MockMLXClient")
    return mock_class(MLXSettings())


def _import_mock_class(dotted_path: str) -> Type[LLMClientProtocol]:
    """Dynamically import a mock class from a dotted path."""
    module_name, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_name)
    mock_class: Type[LLMClientProtocol] = getattr(module, class_name)
    return mock_class


# Client factory registries
CLIENT_FACTORIES: dict[str, ClientFactory] = {
    "ollama": _create_ollama_client,
    "mlx": _create_mlx_client,
}

MOCK_FACTORIES: dict[str, MockFactory] = {
    "ollama": _create_mock_ollama_client,
    "mlx": _create_mock_mlx_client,
}


@lru_cache()
def get_app_settings() -> NexusSettings:
    """Return singleton NexusSettings instance.

    Cached to ensure settings are loaded only once per application lifecycle.
    """
    return NexusSettings()


def get_llm_client(
    settings: NexusSettings = Depends(get_app_settings),
) -> LLMClientProtocol:
    """Provide the appropriate LLM client based on application settings.

    This function serves as a FastAPI dependency provider. It selects and
    instantiates the correct LLM client (real or mock) based on the configured
    backend and mock settings.

    Args:
        settings: Application settings, injected by FastAPI.

    Returns:
        An instance of the configured LLM client.

    Raises:
        ValueError: If an unknown backend is configured and fallback fails.
    """
    backend = (settings.llm_backend or "ollama").lower()

    # Determine if we should use a mock client
    mock_flags = {
        "ollama": settings.use_mock_ollama,
        "mlx": settings.use_mock_mlx,
    }
    use_mock = mock_flags.get(backend, False)

    # Select the appropriate factory
    factory_registry = MOCK_FACTORIES if use_mock else CLIENT_FACTORIES
    factory = factory_registry.get(backend)

    if factory is None:
        LOGGER.warning("Unknown LLM backend '%s'. Falling back to Ollama.", backend)
        # Fallback to Ollama
        fallback_registry = (
            MOCK_FACTORIES if settings.use_mock_ollama else CLIENT_FACTORIES
        )
        factory = fallback_registry.get("ollama")

    if factory is None:
        msg = "Failed to create LLM client: no factory available"
        raise ValueError(msg)

    return factory(settings)
