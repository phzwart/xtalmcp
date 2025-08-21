"""
YAML configuration validation utility for XtalMCP.

This module provides simple validation functions that use Pydantic models
to ensure YAML configuration files are properly formatted and contain
all required fields.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Union, List
import logging

from .models import ToolRegistryConfiguration, ToolConfiguration

logger = logging.getLogger(__name__)


class ConfigurationValidationError(Exception):
    """Raised when YAML configuration validation fails."""
    
    def __init__(self, message: str, errors: List[str] = None):
        super().__init__(message)
        self.errors = errors or []
    
    def __str__(self):
        if self.errors:
            return f"{super().__str__()}\nValidation errors:\n" + "\n".join(f"  - {error}" for error in self.errors)
        return super().__str__()


def validate_yaml_config(config_data: Dict[str, Any]) -> ToolRegistryConfiguration:
    """
    Validate a YAML configuration dictionary.
    
    Args:
        config_data: Dictionary loaded from YAML file
        
    Returns:
        Validated ToolRegistryConfiguration object
        
    Raises:
        ConfigurationValidationError: If validation fails
    """
    try:
        # Use Pydantic to validate the configuration
        config = ToolRegistryConfiguration(**config_data)
        logger.info("Configuration validation successful")
        return config
        
    except Exception as e:
        # Extract validation errors from Pydantic
        if hasattr(e, 'errors'):
            errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
            raise ConfigurationValidationError(
                f"Configuration validation failed: {str(e)}", 
                errors
            )
        else:
            raise ConfigurationValidationError(f"Configuration validation failed: {str(e)}")


def validate_yaml_file(file_path: Union[str, Path]) -> ToolRegistryConfiguration:
    """
    Load and validate a YAML configuration file.
    
    Args:
        file_path: Path to the YAML configuration file
        
    Returns:
        Validated ToolRegistryConfiguration object
        
    Raises:
        ConfigurationValidationError: If validation fails
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            
        if config_data is None:
            raise ConfigurationValidationError("YAML file is empty or contains no data")
            
        return validate_yaml_config(config_data)
        
    except yaml.YAMLError as e:
        raise ConfigurationValidationError(f"Invalid YAML format: {str(e)}")
    except Exception as e:
        if isinstance(e, ConfigurationValidationError):
            raise
        raise ConfigurationValidationError(f"Error reading configuration file: {str(e)}")


def validate_tool_config(tool_name: str, tool_data: Dict[str, Any]) -> ToolConfiguration:
    """
    Validate a single tool configuration.
    
    Args:
        tool_name: Name of the tool (for error reporting)
        tool_data: Tool configuration dictionary
        
    Returns:
        Validated ToolConfiguration object
        
    Raises:
        ConfigurationValidationError: If validation fails
    """
    try:
        tool_config = ToolConfiguration(**tool_data)
        logger.debug(f"Tool '{tool_name}' validation successful")
        return tool_config
        
    except Exception as e:
        if hasattr(e, 'errors'):
            errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
            raise ConfigurationValidationError(
                f"Tool '{tool_name}' validation failed: {str(e)}", 
                errors
            )
        else:
            raise ConfigurationValidationError(f"Tool '{tool_name}' validation failed: {str(e)}")


def get_configuration_schema() -> Dict[str, Any]:
    """
    Get the JSON schema for tool configuration files.
    
    Returns:
        JSON schema dictionary that can be used for validation
    """
    return ToolRegistryConfiguration.schema()


def get_tool_schema() -> Dict[str, Any]:
    """
    Get the JSON schema for individual tool configurations.
    
    Returns:
        JSON schema dictionary for tool configuration
    """
    return ToolConfiguration.schema()


def print_configuration_help():
    """Print help information about configuration format."""
    print("XtalMCP Tool Configuration Format")
    print("=" * 40)
    print()
    
    # Print required fields
    print("REQUIRED FIELDS:")
    print("  - module: Python module path (e.g., 'my_package.tools')")
    print("  - function: Function or class name within the module")
    print("  - description: Human-readable description of the tool")
    print()
    
    # Print optional fields
    print("OPTIONAL FIELDS:")
    print("  - auto_schema: Whether to auto-detect schemas (default: false)")
    print("  - file_input: Whether tool handles file inputs (default: false)")
    print("  - input_schema: Custom input schema definition")
    print("  - output_schema: Custom output schema definition")
    print("  - version: Tool version string")
    print("  - author: Tool author/maintainer")
    print("  - tags: List of tags for categorization")
    print()
    
    # Print examples
    print("EXAMPLE CONFIGURATION:")
    print("tools:")
    print("  my_tool:")
    print("    module: 'my_package.tools'")
    print("    function: 'MyTool'")
    print("    description: 'A description of what my tool does'")
    print("    auto_schema: true")
    print("    file_input: false")
    print()
    
    print("For a complete template, see: src/xtalmcp/registry/templates/tool_config_template.yaml")
    print("For detailed schema information, use: get_configuration_schema()") 