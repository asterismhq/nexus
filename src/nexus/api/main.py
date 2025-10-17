"""FastAPI application entry point for the template."""

from importlib import metadata

from fastapi import FastAPI

from .router import router


def get_app_version(package_name: str, fallback_version: str = "0.1.0") -> str:
    """
    Safely retrieve the version of a package.
    Args:
        package_name: The package name (e.g., "nexus")
        fallback_version: Default version if retrieval fails
    Returns:
        Version string
    """
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return fallback_version


app = FastAPI(
    title="Nexus API",
    description="Configurable FastAPI service that mediates LLM inference",
    version=get_app_version("nexus"),
)
app.include_router(router)
