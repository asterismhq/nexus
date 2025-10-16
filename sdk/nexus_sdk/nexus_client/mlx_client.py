from __future__ import annotations

from .base_client import BaseNexusClient


class NexusMLXClient(BaseNexusClient):
    """HTTP client targeting the Nexus API with the MLX backend."""

    def __init__(
        self,
        base_url: str,
        response_format: str = "dict",
        timeout: float = 10.0,
    ) -> None:
        super().__init__(
            base_url=base_url,
            response_format=response_format,
            timeout=timeout,
            backend="mlx",
        )
