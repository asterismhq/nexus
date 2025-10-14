"""Configuration module exposed by the template."""

from .app_settings import AppSettings, settings
from .mlx_settings import MLXSettings
from .ollama_settings import OllamaSettings

__all__ = ["AppSettings", "MLXSettings", "OllamaSettings", "settings"]
