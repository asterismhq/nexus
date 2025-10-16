"""FastAPI application entry point for the template."""

from fastapi import FastAPI

from .router import router

app = FastAPI(title="nexus", version="0.1.0")
app.include_router(router)
