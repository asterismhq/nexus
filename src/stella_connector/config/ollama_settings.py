"""Settings for configuring the Ollama client."""

from pydantic_settings import BaseSettings


class OllamaSettings(BaseSettings):
    """Configuration for interacting with an Ollama deployment."""

    host: str = "http://localhost"
    port: int = 11434
    model: str = "llama3"

    @property
    def base_url(self) -> str:
        """Return the fully qualified base URL for the Ollama service."""

        host = self.host.rstrip("/")
        return f"{host}:{self.port}"
