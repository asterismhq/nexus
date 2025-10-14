"""FastAPI application entry point for the template."""

from fastapi import FastAPI

from ..container import container
from .router import router

app = FastAPI(title="fapi-tmpl", version="0.1.0")
app.state.container = container
app.include_router(router)
