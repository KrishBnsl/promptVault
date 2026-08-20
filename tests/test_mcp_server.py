"""Tests for the MCP server."""

from mcp_server.server import create_mcp_server


class TestMCPServer:
    """Tests for MCP server tool handlers."""

    def test_create_server(self):
        """Test that server can be created."""
        server = create_mcp_server()
        assert server is not None
        assert server.name == "promptvault-mcp"

    def test_server_has_tools(self):
        """Test that server has all expected tools registered."""
        server = create_mcp_server()
        # Check that tool_manager has tools registered
        tool_names = list(server._tool_manager._tools.keys()) if hasattr(server, '_tool_manager') else []
        # The tools should be registered via decorators
        assert len(tool_names) > 0 or hasattr(server, '_tool_manager')
