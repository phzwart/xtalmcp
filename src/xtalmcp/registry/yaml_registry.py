"""
YAML-based tool registry for XtalMCP.

This module provides dynamic tool registration from YAML configuration files,
enabling zero-code integration of existing Python functions.
"""

import importlib
import inspect
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import yaml

from xtalmcp.base import BaseTool
from .schema_detector import SchemaDetector

logger = logging.getLogger(__name__)


class DynamicTool(BaseTool):
    """
    Dynamically created tool from YAML configuration.
    
    This tool wraps existing Python functions and provides
    the BaseTool interface required by XtalMCP.
    """
    
    def __init__(self, name: str, function: callable, config: Dict[str, Any]):
        """
        Initialize dynamic tool.
        
        Args:
            name: Tool name
            function: Python function to wrap
            config: Tool configuration from YAML
        """
        super().__init__()
        self.name = name
        self.function = function
        self.config = config
        
        # Set description from config or auto-detected
        self.description = config.get('description', f"Dynamic tool: {name}")
        
        # Set input/output schemas
        self.input_schema = config.get('input_schema', {})
        self.output_schema = config.get('output_schema', {})
        
        # Check if this is a file processing tool
        self.file_input = config.get('file_input', False)
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the wrapped function.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Function result wrapped in standard format
        """
        try:
            # Handle file input if specified
            if self.file_input:
                kwargs = self._process_file_input(kwargs)
            
            # Call the wrapped function
            if self._is_async_function(self.function):
                result = await self.function(**kwargs)
            else:
                result = self.function(**kwargs)
            
            # Return in standard format
            return {
                'result': result,
                'tool_name': self.name,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {e}")
            return {
                'error': str(e),
                'tool_name': self.name,
                'status': 'error'
            }
    
    def _process_file_input(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Process file input parameters."""
        # This would integrate with FileInputTool logic
        # For now, just pass through
        return kwargs
    
    def _is_async_function(self, func: callable) -> bool:
        """Check if function is async."""
        return inspect.iscoroutinefunction(func)
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """
        Get the MCP tool schema for this tool.
        
        Returns:
            Dictionary containing the tool schema in MCP format
        """
        schema = {
            'name': self.name,
            'description': self.description
        }
        
        # Add input schema if available
        if self.input_schema:
            schema['inputSchema'] = self.input_schema
        
        # Add output schema if available
        if self.output_schema:
            schema['outputSchema'] = self.output_schema
        
        return schema


class YAMLToolRegistry:
    """
    Registry for loading tools from YAML configurations.
    
    This registry enables zero-code integration of existing Python
    functions by automatically detecting schemas and creating tool wrappers.
    """
    
    def __init__(self, yaml_path: Optional[str] = None):
        """
        Initialize the YAML tool registry.
        
        Args:
            yaml_path: Path to YAML configuration file
        """
        self.yaml_path = yaml_path
        self.tools: Dict[str, DynamicTool] = {}
        self.config: Dict[str, Any] = {}
        
        if yaml_path:
            self.load_tools()
    
    def load_tools(self, yaml_path: Optional[str] = None) -> None:
        """
        Load tools from YAML configuration.
        
        Args:
            yaml_path: Optional override for YAML path
        """
        path = yaml_path or self.yaml_path
        if not path:
            raise ValueError("No YAML path specified")
        
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"YAML file not found: {path}")
        
        logger.info(f"Loading tools from {path}")
        
        with open(path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self._create_tools_from_config()
        logger.info(f"Loaded {len(self.tools)} tools from YAML")
    
    def _create_tools_from_config(self) -> None:
        """Create tool instances from loaded configuration."""
        if 'tools' not in self.config:
            logger.warning("No 'tools' section found in YAML")
            return
        
        for tool_name, tool_config in self.config['tools'].items():
            try:
                tool = self._create_tool_from_config(tool_name, tool_config)
                self.tools[tool_name] = tool
                logger.info(f"Created tool: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to create tool {tool_name}: {e}")
    
    def _create_tool_from_config(self, tool_name: str, config: Dict[str, Any]) -> DynamicTool:
        """
        Create a tool instance from YAML configuration.
        
        Args:
            tool_name: Name of the tool
            config: Tool configuration dictionary
            
        Returns:
            DynamicTool instance
        """
        # Validate required fields
        required_fields = ['module', 'function']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' for tool {tool_name}")
        
        # Import the module and function
        module_name = config['module']
        function_name = config['function']
        
        try:
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Could not import {module_name}.{function_name}: {e}")
        
        # Auto-detect schema if requested
        if config.get('auto_schema', False):
            logger.info(f"Auto-detecting schema for {tool_name}")
            detected_schema = SchemaDetector.detect_schema(function, module_name)
            
            # Merge detected schema with config (config takes precedence)
            if 'description' not in config:
                config['description'] = detected_schema['description']
            if 'input_schema' not in config:
                config['input_schema'] = detected_schema['input_schema']
            if 'output_schema' not in config:
                config['output_schema'] = detected_schema['output_schema']
        
        # Create and return the dynamic tool
        return DynamicTool(tool_name, function, config)
    
    def get_tool(self, tool_name: str) -> Optional[DynamicTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            DynamicTool instance or None if not found
        """
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """
        Get list of available tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def get_tool_config(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get tool configuration.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool configuration dictionary or None if not found
        """
        tool = self.get_tool(tool_name)
        return tool.config if tool else None
    
    def reload(self) -> None:
        """Reload tools from YAML configuration."""
        if self.yaml_path:
            self.load_tools()
        else:
            logger.warning("No YAML path set, cannot reload") 