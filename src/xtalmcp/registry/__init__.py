"""
XtalMCP Registry Package.

This package provides tools for dynamically registering and managing
crystallography tools from YAML configurations.
"""

from .yaml_registry import YAMLToolRegistry
from .schema_detector import SchemaDetector
from .models import (
    ToolRegistryConfiguration, 
    ToolConfiguration, 
    JSONSchema,
    CrystallographySchema,
    CommonParameters,
    # Enums
    OutputFormat,
    ValidationLevel,
    CrystallographicSystem,
    SpaceGroupNotation,
    FileFormat,
    DataType
)
from .validator import (
    validate_yaml_config, 
    validate_yaml_file, 
    validate_tool_config,
    get_configuration_schema,
    get_tool_schema,
    print_configuration_help,
    ConfigurationValidationError
)

__all__ = [
    "YAMLToolRegistry", 
    "SchemaDetector",
    "ToolRegistryConfiguration",
    "ToolConfiguration", 
    "JSONSchema",
    "CrystallographySchema",
    "CommonParameters",
    # Enums
    "OutputFormat",
    "ValidationLevel", 
    "CrystallographicSystem",
    "SpaceGroupNotation",
    "FileFormat",
    "DataType",
    # Validation functions
    "validate_yaml_config",
    "validate_yaml_file",
    "validate_tool_config",
    "get_configuration_schema",
    "get_tool_schema",
    "print_configuration_help",
    "ConfigurationValidationError"
] 