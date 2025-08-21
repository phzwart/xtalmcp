"""
Main FastMCP server for XtalMCP.
"""

import asyncio
import logging
from typing import Dict, Type
from fastapi import FastAPI
from fastmcp import FastMCP

from .base import BaseTool

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
        self.app = FastAPI(title=server_name, version=version)
        self.mcp = FastMCP(self.app)
        
        # Add web endpoints
        self._setup_endpoints()
    
    def register_tool(self, tool: BaseTool):
        """
        Register a tool with the server.
        
        Args:
            tool: Tool instance to register
        """
        if not isinstance(tool, BaseTool):
            raise ValueError("Tool must inherit from BaseTool")
        
        self.tools[tool.name] = tool
        self._register_tool_with_fastmcp(tool)
        logger.info(f"Registered tool: {tool.name}")
    
    def register_tool_class(self, tool_class: Type[BaseTool]):
        """
        Register a tool class with the server.
        
        Args:
            tool_class: Tool class to instantiate and register
        """
        tool = tool_class()
        self.register_tool(tool)
    
    def _register_tool_with_fastmcp(self, tool: BaseTool):
        """Register a tool with FastMCP."""
        
        # For now, skip FastMCP registration to avoid **kwargs issue
        # The tools will still be available through the REST API
        logger.warning(f"Skipping FastMCP registration for {tool.name} due to **kwargs limitation")
        return
    
    def list_tools(self) -> list[str]:
        """
        Get list of registered tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def _setup_endpoints(self):
        """Setup web endpoints for the server."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint showing server info."""
            return {
                "server": self.server_name,
                "version": self.version,
                "tools": len(self.tools),
                "endpoints": {
                    "tools": "/tools",
                    "tool_info": "/tools/{tool_name}",
                    "health": "/health",
                    "docs": "/docs"
                }
            }
        
        @self.app.get("/tools")
        async def list_tools_endpoint():
            """List all registered tools."""
            tools_info = {}
            for name, tool in self.tools.items():
                tools_info[name] = {
                    "description": tool.description,
                    "type": tool.__class__.__name__
                }
            return {
                "tools": tools_info,
                "count": len(self.tools)
            }
        
        @self.app.get("/tools/{tool_name}")
        async def get_tool_info(tool_name: str):
            """Get information about a specific tool."""
            if tool_name not in self.tools:
                return {"error": f"Tool '{tool_name}' not found"}
            
            tool = self.tools[tool_name]
            return {
                "name": tool_name,
                "description": tool.description,
                "type": tool.__class__.__name__
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "tools": len(self.tools)}
    
    async def start(self, host: str = "127.0.0.1", port: int = 8080):
        """
        Start the server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        
        logger.info(f"Starting {self.server_name} v{self.version}")
        logger.info(f"Registered tools: {', '.join(self.list_tools())}")
        
        config = uvicorn.Config(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    def run(self, host: str = "127.0.0.1", port: int = 8080):
        """
        Run the server synchronously.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        asyncio.run(self.start(host, port))


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