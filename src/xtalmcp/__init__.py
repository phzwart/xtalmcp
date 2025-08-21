"""
XtalMCP - A minimal FastMCP server example.

This package provides a minimal FastMCP server with a hello world tool.
"""

__version__ = "1.0.0"
__author__ = "PHZwart <phzwart@lbl.gov>"

from .server import XtalMCPServer, create_server
from .base import BaseTool

__all__ = ["XtalMCPServer", "BaseTool", "create_server"]
