"""Integration tests for the MCP server."""

import json
import os
import sys

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_stdio_server_tools_and_resources(tmp_path):
    """A real client can initialize, call tools, and read resources."""
    env = dict(os.environ)
    env["PROMPTVAULT_DB_PATH"] = str(tmp_path / "mcp.sqlite")
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"],
        env=env,
        cwd=os.getcwd(),
    )

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            templates = await session.list_resource_templates()

            assert initialized.server_info.name == "pvlt-mcp"
            assert "prompt_update" in {tool.name for tool in tools.tools}
            assert len(templates.resource_templates) == 4
            create_tool = next(tool for tool in tools.tools if tool.name == "prompt_create")
            assert "model_config" in create_tool.input_schema["properties"]
            assert "kwargs" not in create_tool.input_schema["properties"]

            result = await session.call_tool(
                "prompt_create",
                {
                    "name": "greeting",
                    "content": "Hello {name}",
                    "model_config": {"provider": "ollama"},
                },
            )
            assert not result.is_error
            payload = json.loads(result.content[0].text)
            assert payload["version"] == 1

            resource = await session.read_resource("prompt://greeting/latest")
            resource_payload = json.loads(resource.contents[0].text)
            assert resource_payload["content"] == "Hello {name}"
            assert resource_payload["model_config"] == {"provider": "ollama"}
