"""Configuration module exposed by the template."""

from .mlx_settings import MLXSettings
from .nexus_settings import NexusSettings, settings
from .ollama_settings import OllamaSettings
from .vllm_settings import VLLMSettings

__all__ = [
    "NexusSettings",
    "MLXSettings",
    "OllamaSettings",
    "VLLMSettings",
    "settings",
]
