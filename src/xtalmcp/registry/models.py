"""
Pydantic models for XtalMCP tool configuration validation.

These models define the structure and validation rules for tool configuration files.
Users can reference these models to understand exactly what fields are required
and what their expected types and values are.
"""

from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class OutputFormat(str, Enum):
    """Valid output formats for tools."""
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"


class ValidationLevel(str, Enum):
    """Validation levels for structure validation tools."""
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"


class CrystallographicSystem(str, Enum):
    """Crystallographic crystal systems."""
    TRICLINIC = "triclinic"
    MONOCLINIC = "monoclinic"
    ORTHORHOMBIC = "orthorhombic"
    TETRAGONAL = "tetragonal"
    TRIGONAL = "trigonal"
    HEXAGONAL = "hexagonal"
    CUBIC = "cubic"


class SpaceGroupNotation(str, Enum):
    """Common space group notation systems."""
    HALL = "hall"
    HERMANN_MAUGUIN = "hermann_mauguin"
    SCHOENFLIES = "schoenflies"
    SHORT = "short"


class FileFormat(str, Enum):
    """Common crystallography file formats."""
    CIF = "cif"
    PDB = "pdb"
    MTZ = "mtz"
    SCALA = "scala"
    AIMLESS = "aimless"
    PHENIX = "phenix"
    CCP4 = "ccp4"
    TEXT = "text"
    CSV = "csv"
    JSON = "json"
    YAML = "yaml"


class DataType(str, Enum):
    """Common data types for crystallography tools."""
    INTENSITY = "intensity"
    AMPLITUDE = "amplitude"
    PHASE = "phase"
    UNIT_CELL = "unit_cell"
    SPACE_GROUP = "space_group"
    ATOMIC_COORDINATES = "atomic_coordinates"
    B_FACTORS = "b_factors"
    OCCUPANCY = "occupancy"
    RESOLUTION = "resolution"
    CORRELATION = "correlation"
    STATISTICS = "statistics"


class JSONSchema(BaseModel):
    """JSON Schema definition for tool input/output validation."""
    type: str = Field(..., description="Schema type (object, string, integer, etc.)")
    properties: Optional[Dict[str, Any]] = Field(None, description="Object properties")
    required: Optional[List[str]] = Field(None, description="Required properties")
    description: Optional[str] = Field(None, description="Property description")
    enum: Optional[List[Any]] = Field(None, description="Allowed values")
    default: Optional[Any] = Field(None, description="Default value")
    minimum: Optional[Union[int, float]] = Field(None, description="Minimum value")
    maximum: Optional[Union[int, float]] = Field(None, description="Maximum value")
    pattern: Optional[str] = Field(None, description="Regex pattern for strings")
    format: Optional[str] = Field(None, description="Data format (email, uri, etc.)")
    items: Optional[Union['JSONSchema', List['JSONSchema']]] = Field(None, description="Schema for array items")
    additional_properties: Optional[Union[bool, 'JSONSchema']] = Field(None, description="Additional properties allowed")
    one_of: Optional[List['JSONSchema']] = Field(None, description="Schema must match one of these")
    any_of: Optional[List['JSONSchema']] = Field(None, description="Schema must match any of these")
    all_of: Optional[List['JSONSchema']] = Field(None, description="Schema must match all of these")
    not_: Optional['JSONSchema'] = Field(None, description="Schema must not match this", alias="not")
    if_: Optional['JSONSchema'] = Field(None, description="Conditional validation", alias="if")
    then: Optional['JSONSchema'] = Field(None, description="Schema to apply if condition is met")
    else_: Optional['JSONSchema'] = Field(None, description="Schema to apply if condition is not met", alias="else")
    const: Optional[Any] = Field(None, description="Value must exactly match this constant")
    examples: Optional[List[Any]] = Field(None, description="Example values")
    read_only: Optional[bool] = Field(None, description="Property is read-only")
    write_only: Optional[bool] = Field(None, description="Property is write-only")
    deprecated: Optional[bool] = Field(None, description="Property is deprecated")


class CrystallographySchema(BaseModel):
    """Specialized schema components for crystallography tools."""
    
    # Unit cell parameters
    unit_cell: Optional[JSONSchema] = Field(
        None, 
        description="Schema for unit cell parameters (a, b, c, α, β, γ)"
    )
    
    # Space group
    space_group: Optional[JSONSchema] = Field(
        None, 
        description="Schema for space group information"
    )
    
    # Resolution range
    resolution_range: Optional[JSONSchema] = Field(
        None, 
        description="Schema for resolution range (min, max)"
    )
    
    # File input/output
    file_input: Optional[JSONSchema] = Field(
        None, 
        description="Schema for file input parameters"
    )
    
    # Data quality metrics
    quality_metrics: Optional[JSONSchema] = Field(
        None, 
        description="Schema for data quality metrics (R-factor, CC, etc.)"
    )
    
    # Atomic coordinates
    atomic_coordinates: Optional[JSONSchema] = Field(
        None, 
        description="Schema for atomic coordinate data"
    )
    
    # Reflection data
    reflection_data: Optional[JSONSchema] = Field(
        None, 
        description="Schema for reflection data (h, k, l, intensity, etc.)"
    )


class ToolConfiguration(BaseModel):
    """
    Configuration for a single tool.
    
    This model defines all possible configuration options for tools.
    Required fields: module, function, description
    Optional fields: auto_schema, file_input, input_schema, output_schema
    """
    
    # Required fields
    module: str = Field(
        ..., 
        description="Python module path to import the tool from (e.g., 'my_package.tools')"
    )
    function: str = Field(
        ..., 
        description="Function or class name within the module to use as the tool"
    )
    description: str = Field(
        ..., 
        description="Human-readable description of what the tool does"
    )
    
    # Optional fields
    auto_schema: bool = Field(
        False, 
        description="Whether to automatically detect input/output schemas from type hints"
    )
    file_input: bool = Field(
        False, 
        description="Whether this tool processes file inputs (enables file handling)"
    )
    
    # Custom schema definitions (override auto_schema when provided)
    input_schema: Optional[Union[JSONSchema, CrystallographySchema]] = Field(
        None, 
        description="Custom input schema definition (overrides auto_schema)"
    )
    output_schema: Optional[Union[JSONSchema, CrystallographySchema]] = Field(
        None, 
        description="Custom output schema definition (overrides auto_schema)"
    )
    
    # Tool-specific configuration
    tool_type: Optional[str] = Field(
        None, 
        description="Type of tool (e.g., 'data_processing', 'visualization', 'validation')"
    )
    
    # Dependencies and requirements
    dependencies: Optional[List[str]] = Field(
        None, 
        description="List of required Python packages or external tools"
    )
    
    # Runtime configuration
    timeout: Optional[int] = Field(
        None, 
        description="Tool execution timeout in seconds"
    )
    
    memory_limit: Optional[str] = Field(
        None, 
        description="Memory limit for tool execution (e.g., '1GB', '512MB')"
    )
    
    # Execution environment
    environment: Optional[Dict[str, str]] = Field(
        None, 
        description="Environment variables to set for tool execution"
    )
    
    # Additional metadata
    version: Optional[str] = Field(
        None, 
        description="Tool version string"
    )
    author: Optional[str] = Field(
        None, 
        description="Tool author or maintainer"
    )
    tags: Optional[List[str]] = Field(
        None, 
        description="Tags for categorizing the tool"
    )
    
    @field_validator('auto_schema')
    @classmethod
    def validate_auto_schema_conflict(cls, v, info):
        """Ensure auto_schema and custom schemas don't conflict."""
        if v and (info.data.get('input_schema') or info.data.get('output_schema')):
            raise ValueError(
                "auto_schema=True conflicts with custom schema definitions. "
                "Set auto_schema=False when providing custom schemas."
            )
        return v
    
    @field_validator('module')
    @classmethod
    def validate_module_path(cls, v):
        """Validate module path format."""
        if not v:
            raise ValueError("Module path cannot be empty")
        # Allow both single modules (e.g., 'numpy') and dotted paths (e.g., 'package.module')
        return v
    
    @field_validator('function')
    @classmethod
    def validate_function_name(cls, v):
        """Validate function/class name."""
        if not v or not v.replace('_', '').isalnum():
            raise ValueError("Function name must be alphanumeric with underscores only")
        return v


class ToolRegistryConfiguration(BaseModel):
    """
    Complete tool registry configuration file.
    
    This is the root model for YAML configuration files.
    """
    
    # Metadata
    version: str = Field(
        "1.0", 
        description="Configuration file version"
    )
    description: Optional[str] = Field(
        None, 
        description="Overall description of this tool collection"
    )
    
    # Tool definitions
    tools: Dict[str, ToolConfiguration] = Field(
        ..., 
        description="Dictionary of tool configurations, keyed by tool name"
    )
    
    # Global settings
    auto_reload: bool = Field(
        False, 
        description="Whether to automatically reload tools when files change"
    )
    default_format: Optional[str] = Field(
        None, 
        description="Default output format for tools"
    )
    
    @field_validator('tools')
    @classmethod
    def validate_tool_names(cls, v):
        """Validate tool names are valid identifiers."""
        for tool_name in v.keys():
            if not tool_name or not tool_name.replace('_', '').isalnum():
                raise ValueError(
                    f"Tool name '{tool_name}' must be alphanumeric with underscores only"
                )
        return v


# Common parameter type definitions for crystallography tools
class CommonParameters:
    """Common parameter schemas that crystallography tools can reference."""
    
    @staticmethod
    def file_path(description: str = "Path to input file") -> JSONSchema:
        """Schema for file path parameters."""
        return JSONSchema(
            type="string",
            description=description,
            pattern=r"^[^<>:\"|?*]+$"  # Basic file path validation
        )
    
    @staticmethod
    def unit_cell() -> JSONSchema:
        """Schema for unit cell parameters."""
        return JSONSchema(
            type="object",
            properties={
                "a": JSONSchema(type="number", minimum=0, description="Unit cell length a (Å)"),
                "b": JSONSchema(type="number", minimum=0, description="Unit cell length b (Å)"),
                "c": JSONSchema(type="number", minimum=0, description="Unit cell length c (Å)"),
                "alpha": JSONSchema(type="number", minimum=0, maximum=180, description="Unit cell angle α (degrees)"),
                "beta": JSONSchema(type="number", minimum=0, maximum=180, description="Unit cell angle β (degrees)"),
                "gamma": JSONSchema(type="number", minimum=0, maximum=180, description="Unit cell angle γ (degrees)")
            },
            required=["a", "b", "c", "alpha", "beta", "gamma"]
        )
    
    @staticmethod
    def resolution_range() -> JSONSchema:
        """Schema for resolution range parameters."""
        return JSONSchema(
            type="object",
            properties={
                "min": JSONSchema(type="number", minimum=0, description="Minimum resolution (Å)"),
                "max": JSONSchema(type="number", minimum=0, description="Maximum resolution (Å)")
            },
            required=["min", "max"]
        )
    
    @staticmethod
    def space_group() -> JSONSchema:
        """Schema for space group parameters."""
        return JSONSchema(
            type="string",
            description="Space group symbol or number",
            examples=["P1", "P21", "P212121", "F432", "225"]
        )
    
    @staticmethod
    def output_format(formats: List[str] = None) -> JSONSchema:
        """Schema for output format parameters."""
        if formats is None:
            formats = ["json", "csv", "text", "yaml"]
        return JSONSchema(
            type="string",
            enum=formats,
            default="json",
            description="Output format for results"
        )


# Example configurations for documentation
EXAMPLE_TOOL_CONFIG = ToolConfiguration(
    module="my_package.tools",
    function="MyCrystallographyTool",
    description="A tool for processing crystallography data",
    auto_schema=True,
    file_input=True,
    version="1.0.0",
    author="Dr. Scientist",
    tags=["crystallography", "data-processing"],
    tool_type="data_processing",
    dependencies=["numpy", "scipy"],
    timeout=300,
    memory_limit="1GB"
)

EXAMPLE_REGISTRY_CONFIG = ToolRegistryConfiguration(
    version="1.0",
    description="My crystallography tools collection",
    tools={
        "my_tool": EXAMPLE_TOOL_CONFIG
    },
    auto_reload=True,
    default_format="json"
) 