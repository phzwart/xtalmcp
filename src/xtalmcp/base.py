"""
Base classes for XtalMCP tools.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """
    Base class for all XtalMCP tools.
    
    This class provides the minimal interface that all tools must implement.
    Tools should inherit from this class and implement the required methods.
    """
    
    def __init__(self):
        self.name: str = self.__class__.__name__.lower()
        self.description: str = "A simple tool"
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Dict containing the tool's output
        """
        pass
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """
        Get the tool schema for MCP registration.
        
        Returns:
            Dict containing the tool's basic schema
        """
        return {
            "name": self.name,
            "description": self.description,
        }
    
    async def run(self, **kwargs) -> Dict[str, Any]:
        """
        Run the tool with basic error handling.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Dict containing the tool's output
        """
        try:
            return await self.execute(**kwargs)
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "tool": self.name
            }


class FileInputTool(BaseTool):
    """
    Base class for tools that work with file inputs.
    
    Provides common functionality for tools that need to read files.
    """
    
    def __init__(self):
        super().__init__()
        self.description = "A file processing tool"
    
    async def get_file_content(self, file_path: str = None, content: str = None) -> str:
        """
        Get file content from either file path or direct content.
        
        Args:
            file_path: Path to the file
            content: Direct file content
            
        Returns:
            File content as string
        """
        if content:
            return content
        elif file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                raise ValueError(f"Could not read file {file_path}: {e}")
        else:
            raise ValueError("Either file_path or content must be provided")