"""Test cases for the server module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from xtalmcp.server import XtalMCPServer, create_server
from xtalmcp.base import BaseTool


class TestTool(BaseTool):
    """Test tool for server testing."""
    
    def __init__(self, name: str = "test_tool"):
        super().__init__()
        self.name = name
        self.description = f"Test tool: {name}"
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        return {"result": "test", "tool": self.name}


class TestXtalMCPServer:
    """Test cases for XtalMCPServer class."""
    
    def test_server_initialization(self):
        """Test server initialization."""
        server = XtalMCPServer()
        
        assert server.server_name == "xtalmcp-server"
        assert server.version == "0.1.0"
        assert server.tools == {}
        assert server.app is not None
        assert server.mcp is not None
    
    def test_server_initialization_custom(self):
        """Test server initialization with custom parameters."""
        server = XtalMCPServer("custom-server", "2.0.0")
        
        assert server.server_name == "custom-server"
        assert server.version == "2.0.0"
    
    @patch('xtalmcp.server.FastMCP')
    def test_register_tool(self, mock_fastmcp):
        """Test tool registration."""
        mock_fastmcp_instance = Mock()
        mock_fastmcp.return_value = mock_fastmcp_instance
        
        server = XtalMCPServer()
        tool = TestTool()
        
        server.register_tool(tool)
        
        assert tool.name in server.tools
        assert server.tools[tool.name] == tool
    
    def test_register_tool_invalid_type(self):
        """Test tool registration with invalid type."""
        server = XtalMCPServer()
        
        with pytest.raises(ValueError, match="Tool must inherit from BaseTool"):
            server.register_tool("not_a_tool")
    
    @patch('xtalmcp.server.FastMCP')
    def test_register_tool_class(self, mock_fastmcp):
        """Test tool class registration."""
        mock_fastmcp_instance = Mock()
        mock_fastmcp.return_value = mock_fastmcp_instance
        
        server = XtalMCPServer()
        
        server.register_tool_class(TestTool)
        
        assert "test_tool" in server.tools
        assert isinstance(server.tools["test_tool"], TestTool)
    
    @patch('xtalmcp.server.FastMCP')
    def test_list_tools(self, mock_fastmcp):
        """Test listing registered tools."""
        mock_fastmcp_instance = Mock()
        mock_fastmcp.return_value = mock_fastmcp_instance
        
        server = XtalMCPServer()
        
        # No tools initially
        assert server.list_tools() == []
        
        # Register some tools
        tool1 = TestTool("tool1")
        tool2 = TestTool("tool2")
        
        server.register_tool(tool1)
        server.register_tool(tool2)
        
        tools = server.list_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools
    
    def test_register_tool_with_fastmcp(self):
        """Test tool registration with FastMCP."""
        server = XtalMCPServer()
        tool = TestTool()
        
        # Mock the FastMCP add_tool method
        mock_add_tool = Mock()
        server.mcp.add_tool = mock_add_tool
        
        server.register_tool(tool)
        
        # Verify FastMCP add_tool was called
        mock_add_tool.assert_called_once()
        call_args = mock_add_tool.call_args
        
        # Check that add_tool was called with the right keyword arguments
        assert call_args[1]['fn'] is not None  # fn should be the wrapper function
        assert call_args[1]['name'] == tool.name
        assert call_args[1]['description'] == tool.description
    
    def test_create_server(self):
        """Test create_server factory function."""
        server = create_server()
        
        assert isinstance(server, XtalMCPServer)
        assert server.server_name == "xtalmcp-server"
        assert server.version == "0.1.0"
    
    def test_create_server_custom(self):
        """Test create_server with custom parameters."""
        server = create_server("custom", "3.0.0")
        
        assert server.server_name == "custom"
        assert server.version == "3.0.0"


class TestServerIntegration:
    """Integration tests for server functionality."""
    
    @pytest.mark.asyncio
    @patch('xtalmcp.server.FastMCP')
    async def test_tool_lifecycle(self, mock_fastmcp):
        """Test complete tool lifecycle in server."""
        mock_fastmcp_instance = Mock()
        mock_fastmcp.return_value = mock_fastmcp_instance
        
        server = XtalMCPServer()
        
        # Create and register tool
        tool = TestTool("lifecycle_tool")
        server.register_tool(tool)
        
        # Verify tool is registered
        assert tool.name in server.tools
        assert server.tools[tool.name] == tool
        
        # List tools
        tools = server.list_tools()
        assert tool.name in tools
        
        # Test tool execution
        result = await tool.run()
        assert result['result'] == 'test'
        assert result['tool'] == 'lifecycle_tool'
    
    @patch('xtalmcp.server.FastMCP')
    def test_multiple_tools(self, mock_fastmcp):
        """Test multiple tool registration and management."""
        mock_fastmcp_instance = Mock()
        mock_fastmcp.return_value = mock_fastmcp_instance
        
        server = XtalMCPServer()
        
        # Register multiple tools
        tools = [
            TestTool("tool1"),
            TestTool("tool2"),
            TestTool("tool3")
        ]
        
        for tool in tools:
            server.register_tool(tool)
        
        # Verify all tools are registered
        registered_tools = server.list_tools()
        assert len(registered_tools) == 3
        
        for tool in tools:
            assert tool.name in registered_tools
            assert server.tools[tool.name] == tool
    
    @patch('xtalmcp.server.FastMCP')
    def test_tool_class_registration(self, mock_fastmcp):
        """Test tool class registration workflow."""
        mock_fastmcp_instance = Mock()
        mock_fastmcp.return_value = mock_fastmcp_instance
        
        server = XtalMCPServer()
        
        # Register tool class
        server.register_tool_class(TestTool)
        
        # Verify tool was created and registered
        assert "test_tool" in server.tools
        registered_tool = server.tools["test_tool"]
        
        # Verify tool properties
        assert isinstance(registered_tool, TestTool)
        assert registered_tool.name == "test_tool"
        assert "Test tool: test_tool" in registered_tool.description


class TestServerErrorHandling:
    """Test error handling in server."""
    
    def test_register_invalid_tool_type(self):
        """Test error handling for invalid tool types."""
        server = XtalMCPServer()
        
        invalid_tools = [
            "string",
            123,
            None,
            {},
            []
        ]
        
        for invalid_tool in invalid_tools:
            with pytest.raises(ValueError, match="Tool must inherit from BaseTool"):
                server.register_tool(invalid_tool)
    
    @patch('xtalmcp.server.FastMCP')
    def test_duplicate_tool_registration(self, mock_fastmcp):
        """Test duplicate tool registration behavior."""
        mock_fastmcp_instance = Mock()
        mock_fastmcp.return_value = mock_fastmcp_instance
        
        server = XtalMCPServer()
        
        tool1 = TestTool("duplicate")
        tool2 = TestTool("duplicate")  # Same name
        
        # Register first tool
        server.register_tool(tool1)
        assert "duplicate" in server.tools
        
        # Register second tool (should overwrite)
        server.register_tool(tool2)
        assert "duplicate" in server.tools
        assert server.tools["duplicate"] == tool2  # Second tool should be registered


class TestServerFastMCPIntegration:
    """Test FastMCP integration."""
    
    @patch('xtalmcp.server.FastMCP')
    def test_fastmcp_initialization(self, mock_fastmcp):
        """Test FastMCP initialization."""
        mock_fastmcp_instance = Mock()
        mock_fastmcp.return_value = mock_fastmcp_instance
        
        server = XtalMCPServer()
        
        mock_fastmcp.assert_called_once_with(server.app)
        assert server.mcp == mock_fastmcp_instance
    
    @patch('xtalmcp.server.FastMCP')
    def test_tool_registration_with_fastmcp(self, mock_fastmcp):
        """Test tool registration with FastMCP integration."""
        mock_fastmcp_instance = Mock()
        mock_fastmcp.return_value = mock_fastmcp_instance
        
        server = XtalMCPServer()
        tool = TestTool()
        
        # Register tool
        server.register_tool(tool)
        
        # Verify FastMCP add_tool was called
        mock_fastmcp_instance.add_tool.assert_called_once()
        call_args = mock_fastmcp_instance.add_tool.call_args
        
        # Check that add_tool was called with the right keyword arguments
        assert call_args[1]['fn'] is not None  # fn should be the wrapper function
        assert call_args[1]['name'] == tool.name
        assert call_args[1]['description'] == tool.description 