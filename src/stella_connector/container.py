"""Dependency container for the stella connector service."""

from __future__ import annotations

import importlib
import logging
from typing import Optional, Type

from .clients.mlx_client import MLXClient
from .clients.ollama_client import OllamaClient
from .config import AppSettings, MLXSettings, OllamaSettings, settings
from .protocols.llm_client_protocol import LLMClientProtocol

LOGGER = logging.getLogger(__name__)


class DependencyContainer:
    """Dependency container responsible for wiring runtime services."""

    __slots__ = (
        "app_settings",
        "ollama_settings",
        "mlx_settings",
        "_ollama_client",
        "_mlx_client",
        "_mock_ollama_client",
        "_mock_mlx_client",
    )

    def __init__(
        self,
        app_settings: Optional[AppSettings] = None,
        ollama_settings: Optional[OllamaSettings] = None,
        mlx_settings: Optional[MLXSettings] = None,
    ) -> None:
        self.app_settings = app_settings or AppSettings()
        self.ollama_settings = ollama_settings or OllamaSettings()
        self.mlx_settings = mlx_settings or MLXSettings()

        self._ollama_client: OllamaClient | None = None
        self._mlx_client: MLXClient | None = None
        self._mock_ollama_client: LLMClientProtocol | None = None
        self._mock_mlx_client: LLMClientProtocol | None = None

    @property
    def settings(self) -> AppSettings:
        """Return configured application settings."""

        return self.app_settings

    def provide_llm_client(self) -> LLMClientProtocol:
        """Return the appropriate LLM client based on configuration."""

        backend = (self.app_settings.llm_backend or "").lower()
        if backend == "ollama":
            if self.app_settings.use_mock_ollama:
                return self._get_mock_ollama_client()
            return self._get_ollama_client()

        if backend == "mlx":
            if self.app_settings.use_mock_mlx:
                return self._get_mock_mlx_client()
            return self._get_mlx_client()

        LOGGER.warning("Unknown LLM backend '%s'. Falling back to Ollama.", backend)
        if self.app_settings.use_mock_ollama:
            return self._get_mock_ollama_client()
        return self._get_ollama_client()

    def _get_ollama_client(self) -> OllamaClient:
        if self._ollama_client is None:
            self._ollama_client = OllamaClient(self.ollama_settings)
        return self._ollama_client

    def _get_mlx_client(self) -> MLXClient:
        if self._mlx_client is None:
            self._mlx_client = MLXClient(self.mlx_settings)
        return self._mlx_client

    def _get_mock_ollama_client(self) -> LLMClientProtocol:
        if self._mock_ollama_client is None:
            self._mock_ollama_client = self._create_mock_ollama_client()
        return self._mock_ollama_client

    def _get_mock_mlx_client(self) -> LLMClientProtocol:
        if self._mock_mlx_client is None:
            self._mock_mlx_client = self._create_mock_mlx_client()
        return self._mock_mlx_client

    def _create_mock_ollama_client(self) -> LLMClientProtocol:
        mock_class = self._import_mock_class("dev.mocks.mock_ollama_client.MockOllamaClient")
        return mock_class(self.ollama_settings)

    def _create_mock_mlx_client(self) -> LLMClientProtocol:
        mock_class = self._import_mock_class("dev.mocks.mock_mlx_client.MockMLXClient")
        return mock_class(self.mlx_settings)

    def _import_mock_class(self, dotted_path: str) -> Type[LLMClientProtocol]:
        module_name, class_name = dotted_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        mock_class: Type[LLMClientProtocol] = getattr(module, class_name)
        return mock_class


container = DependencyContainer(settings)
