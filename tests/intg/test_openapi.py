"""Integration tests for OpenAPI documentation."""

import pytest
from fastapi import FastAPI


@pytest.mark.asyncio
async def test_openapi_json_endpoint(app: FastAPI, async_client):
    """Test that /openapi.json returns a valid OpenAPI schema."""
    response = await async_client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()

    # Check that it's a valid OpenAPI schema
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

    # Check that /v1/chat/completions is in the paths
    assert "/v1/chat/completions" in schema["paths"]

    # Check the schema for the endpoint
    invoke_path = schema["paths"]["/v1/chat/completions"]
    assert "post" in invoke_path

    post_operation = invoke_path["post"]
    assert "requestBody" in post_operation
    assert "responses" in post_operation

    # Check that the request body references the correct schema
    request_body = post_operation["requestBody"]
    assert "content" in request_body
    assert "application/json" in request_body["content"]
    schema_ref = request_body["content"]["application/json"]["schema"]
    assert "$ref" in schema_ref
    assert schema_ref["$ref"] == "#/components/schemas/ChatCompletionRequest"

    # Check that the response references the correct schema
    responses = post_operation["responses"]
    assert "200" in responses
    response_200 = responses["200"]
    assert "content" in response_200
    assert "application/json" in response_200["content"]
    resp_schema_ref = response_200["content"]["application/json"]["schema"]
    assert "$ref" in resp_schema_ref
    assert resp_schema_ref["$ref"] == "#/components/schemas/ChatCompletionResponse"


@pytest.mark.asyncio
async def test_docs_endpoint(app: FastAPI, async_client):
    """Test that /docs returns HTML content."""
    response = await async_client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    html_content = response.text
    assert "<!DOCTYPE html>" in html_content
    assert (
        "Swagger" in html_content or "ReDoc" in html_content
    )  # FastAPI uses Swagger by default
