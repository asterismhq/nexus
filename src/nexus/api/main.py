"""FastAPI application entry point for the template."""

from importlib import metadata

from fastapi import FastAPI

from .router import router

app = FastAPI(
    title="Nexus API",
    description="Configurable FastAPI service that mediates LLM inference",
    version=metadata.version("nexus"),
)
app.include_router(router)
