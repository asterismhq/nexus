"""FastAPI application entry point for the template."""

from fastapi import FastAPI

from .router import router

app = FastAPI(
    title="Nexus API",
    description="Configurable FastAPI service that mediates LLM inference",
    version="2.0.3",
)
app.include_router(router)
