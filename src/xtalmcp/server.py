"""
Main FastMCP server for XtalMCP.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Type

from fastmcp import FastMCP
from fastmcp.tools import FunctionTool

from .base import BaseTool
from .registry.yaml_registry import YAMLToolRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class XtalMCPServer:
    """
    Minimal FastMCP server for crystallography tools.
    
    This server provides a simple interface for registering and executing
    crystallography-related tools through the MCP protocol.
    """
    
    def __init__(self, server_name: str = "xtalmcp-server", version: str = "0.1.0"):
        """
        Initialize the XtalMCP server.
        
        Args:
            server_name: Name of the server
            version: Version of the server
        """
        self.server_name = server_name
        self.version = version
        self.tools: Dict[str, BaseTool] = {}
        
        # Initialize FastMCP with the new 2.x API
        # FastMCP 2.x has its own HTTP server, so we don't need a separate FastAPI app
        self.mcp = FastMCP(
            name=server_name,
            version=version
        )
        
        # Note: FastMCP 2.x handles HTTP transport internally
        # We'll use its built-in HTTP server instead of our custom FastAPI setup
    
    def register_tool(self, tool: BaseTool):
        """
        Register a tool with the server.
        
        Args:
            tool: Tool instance to register
        """
        if not isinstance(tool, BaseTool):
            raise ValueError("Tool must inherit from BaseTool")
        
        self.tools[tool.name] = tool
        
        # Only register with FastMCP if not already registered
        if not hasattr(tool, '_mcp_registered'):
            self._register_tool_with_fastmcp(tool)
            tool._mcp_registered = True
        
        logger.info(f"Registered tool: {tool.name}")
    
    def register_tool_class(self, tool_class: Type[BaseTool]):
        """Register a tool class by instantiating it and registering the instance."""
        tool_instance = tool_class()
        self.register_tool(tool_instance)
    
    def load_tools_from_yaml(self, config_path: str):
        """Load tools from a YAML configuration file."""
        registry = YAMLToolRegistry(config_path)
        
        # Register all tools from the registry
        for tool_name, tool_instance in registry.tools.items():
            self.register_tool(tool_instance)
            logger.info(f"Registered YAML tool: {tool_name}")
        
        return len(registry.tools)
    
    def _register_tool_with_fastmcp(self, tool: BaseTool):
        """Register a tool with FastMCP."""
        try:
            # Create a wrapper function that handles the **kwargs properly
            async def tool_wrapper(**kwargs):
                """Wrapper for BaseTool.execute to handle FastMCP integration."""
                logger.info(f"FastMCP tool_wrapper called for {tool.name} with kwargs: {kwargs}")
                try:
                    result = await tool.execute(**kwargs)
                    logger.info(f"Tool {tool.name} execution successful: {result}")
                    
                    # For mcpo compatibility, return just the result value, not the wrapped format
                    if isinstance(result, dict) and 'result' in result and result.get('status') == 'success':
                        actual_result = result['result']
                    elif isinstance(result, dict) and 'error' in result:
                        # If there's an error, raise it so mcpo can handle it properly
                        raise Exception(result['error'])
                    else:
                        # Return the result as-is if it's not in our wrapped format
                        actual_result = result
                    
                    # FastMCP expects structured_content to be a dict, so wrap non-dict values
                    if not isinstance(actual_result, dict):
                        # Wrap the result in a dict with a descriptive key
                        return {"value": actual_result}
                    else:
                        return actual_result
                        
                except Exception as e:
                    logger.error(f"Error executing tool {tool.name}: {e}")
                    # Re-raise the exception for mcpo to handle
                    raise e
            
            # Import FunctionTool for FastMCP 2.x compatibility
            from fastmcp.tools import FunctionTool
            
            # Get the tool's input schema for proper parameter definition
            tool_schema = tool.get_tool_schema()
            input_schema = tool_schema.get('input', {})
            
            logger.info(f"Registering tool {tool.name} with input schema: {input_schema}")
            
            # Create a FunctionTool instance with proper parameters
            function_tool = FunctionTool(
                name=tool.name,
                description=tool.description,
                fn=tool_wrapper,
                parameters=input_schema,  # Use the tool's actual input schema
                output_schema=tool_schema.get('output', {"type": "object"})
            )
            
            # Register the tool with FastMCP
            self.mcp.add_tool(function_tool)
            
            logger.info(f"Successfully registered {tool.name} with FastMCP")
            
        except Exception as e:
            logger.error(f"Failed to register {tool.name} with FastMCP: {e}")
            # Don't fail the entire registration, just log the error
    
    def list_tools(self) -> list[str]:
        """
        Get list of registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def is_tool_registered_with_mcp(self, tool_name: str) -> bool:
        """
        Check if a tool is registered with MCP.
        
        Args:
            tool_name: Name of the tool to check
            
        Returns:
            True if tool is registered with MCP, False otherwise
        """
        try:
            # This is a simple check - in a real implementation you might want
            # to maintain a separate registry of MCP-registered tools
            return tool_name in self.tools
        except Exception:
            return False
    
    def start(self, host: str = "127.0.0.1", port: int = 8080):
        """Start the HTTP server using FastMCP 2.x's built-in HTTP capabilities."""
        logger.info(f"Starting {self.server_name} v{self.version} with HTTP transport")
        logger.info(f"Registered tools: {', '.join(self.tools.keys())}")
        logger.info(f"Server will be available at http://{host}:{port}")
        logger.info("Note: This is an MCP server - use MCP clients to interact with tools")
        
        # Use FastMCP 2.x's built-in HTTP server for MCP protocol
        self.mcp.run(transport='http', host=host, port=port)
    
    def run(self, host: str = "127.0.0.1", port: int = 8080):
        """Run the server (synchronous wrapper around start)."""
        self.start(host=host, port=port)
    
    def run_stdio(self):
        """
        Run the server with MCP stdio transport synchronously.
        
        This is the preferred method for MCP client integration.
        """
        logger.info(f"Starting {self.server_name} v{self.version} with MCP stdio transport")
        logger.info(f"Registered tools: {', '.join(self.list_tools())}")
        logger.info("Server ready for MCP stdio communication")
        
        try:
            # Use a simple approach - just call the FastMCP run method
            # The TaskGroup error might be a FastMCP bug that we can't work around
            self.mcp.run(transport='stdio')
        except Exception as e:
            logger.error(f"Error in MCP stdio transport: {e}")
            logger.error("This might be a FastMCP compatibility issue")
            logger.error("Try using the HTTP server instead: xtalmcp serve --config <config>")
            raise
    
    def run_sse(self, host: str = "127.0.0.1", port: int = 8080):
        """
        Run the server with MCP SSE transport synchronously.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        logger.info(f"Starting {self.server_name} v{self.version} with MCP SSE transport")
        logger.info(f"Registered tools: {', '.join(self.list_tools())}")
        logger.info(f"SSE endpoint: http://{host}:{port}")
        
        try:
            # Use the synchronous run method with SSE transport
            self.mcp.run(transport='sse')
        except Exception as e:
            logger.error(f"Error in MCP SSE transport: {e}")
            raise


def create_server(server_name: str = "xtalmcp-server", version: str = "0.1.0") -> XtalMCPServer:
    """
    Create a new XtalMCP server instance.
    
    Args:
        server_name: Name of the server
        version: Version of the server
        
    Returns:
        XtalMCPServer instance
    """
    return XtalMCPServer(server_name, version)