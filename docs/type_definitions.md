# Type Definitions Reference

This document provides a comprehensive reference for all available type definitions, enums, and schema components that can be used in XtalMCP tool configurations.

## Overview

XtalMCP provides a rich set of type definitions that cover:
- **Basic JSON Schema types** with enhanced validation options
- **Crystallography-specific enums** for common values and constraints
- **Common parameter schemas** that can be reused across tools
- **Specialized schema components** for crystallography data

## Enums

### OutputFormat
Standard output formats for tools.

```python
class OutputFormat(str, Enum):
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"
    JSON = "json"
    YAML = "yaml"
    TEXT = "text"
```

**Usage:**
```yaml
output_format:
  type: "string"
  enum: ["png", "svg", "pdf"]  # Use enum values
  default: "png"
```

### ValidationLevel
Validation rigor levels for structure validation tools.

```python
class ValidationLevel(str, Enum):
    BASIC = "basic"
    STANDARD = "standard"
    STRICT = "strict"
```

**Usage:**
```yaml
validation_level:
  type: "string"
  enum: ["basic", "standard", "strict"]
  default: "standard"
```

### CrystallographicSystem
The seven crystal systems in crystallography.

```python
class CrystallographicSystem(str, Enum):
    TRICLINIC = "triclinic"
    MONOCLINIC = "monoclinic"
    ORTHORHOMBIC = "orthorhombic"
    TETRAGONAL = "tetragonal"
    TRIGONAL = "trigonal"
    HEXAGONAL = "hexagonal"
    CUBIC = "cubic"
```

**Usage:**
```yaml
crystal_system:
  type: "string"
  enum: ["triclinic", "monoclinic", "orthorhombic", "tetragonal", "trigonal", "hexagonal", "cubic"]
  description: "Expected crystal system"
```

### SpaceGroupNotation
Common space group notation systems.

```python
class SpaceGroupNotation(str, Enum):
    HALL = "hall"
    HERMANN_MAUGUIN = "hermann_mauguin"
    SCHOENFLIES = "schoenflies"
    SHORT = "short"
```

**Usage:**
```yaml
notation_system:
  type: "string"
  enum: ["hall", "hermann_mauguin", "schoenflies", "short"]
  default: "hermann_mauguin"
```

### FileFormat
Common crystallography file formats.

```python
class FileFormat(str, Enum):
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
```

**Usage:**
```yaml
input_format:
  type: "string"
  enum: ["cif", "pdb", "mtz"]
  description: "Input file format"
```

### DataType
Common data types for crystallography tools.

```python
class DataType(str, Enum):
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
```

**Usage:**
```yaml
data_type:
  type: "string"
  enum: ["intensity", "amplitude", "phase"]
  description: "Type of data to process"
```

## JSON Schema Types

### Basic Types
The `JSONSchema` class extends standard JSON Schema with additional validation options:

```python
class JSONSchema(BaseModel):
    type: str                                    # Schema type
    properties: Optional[Dict[str, Any]]         # Object properties
    required: Optional[List[str]]                # Required properties
    description: Optional[str]                   # Property description
    enum: Optional[List[Any]]                    # Allowed values
    default: Optional[Any]                       # Default value
    minimum: Optional[Union[int, float]]         # Minimum value
    maximum: Optional[Union[int, float]]         # Maximum value
    pattern: Optional[str]                        # Regex pattern
    format: Optional[str]                         # Data format
    items: Optional[Union['JSONSchema', List['JSONSchema']]]  # Array items
    additional_properties: Optional[Union[bool, 'JSONSchema']]  # Additional properties
    one_of: Optional[List['JSONSchema']]         # Must match one of these
    any_of: Optional[List['JSONSchema']]         # Must match any of these
    all_of: Optional[List['JSONSchema']]         # Must match all of these
    not_: Optional['JSONSchema']                 # Must not match this
    if_: Optional['JSONSchema']                  # Conditional validation
    then: Optional['JSONSchema']                 # Schema if condition met
    else_: Optional['JSONSchema']                # Schema if condition not met
    const: Optional[Any]                         # Exact constant value
    examples: Optional[List[Any]]                # Example values
    read_only: Optional[bool]                    # Read-only property
    write_only: Optional[bool]                   # Write-only property
    deprecated: Optional[bool]                   # Deprecated property
```

### Advanced Schema Features

#### Conditional Validation
```yaml
input_schema:
  type: "object"
  properties:
    data_type: {"type": "string", "enum": ["file", "direct"]}
    file_path: {"type": "string"}
    content: {"type": "string"}
  if:
    properties:
      data_type: {"const": "file"}
  then:
    required: ["file_path"]
  else:
    required: ["content"]
```

#### One-of Validation
```yaml
data_source:
  one_of:
    - {"type": "string", "description": "File path"}
    - {"type": "object", "description": "Direct data"}
```

#### Array Validation
```yaml
check_types:
  type: "array"
  items:
    type: "string"
    enum: ["geometry", "stereochemistry", "occupancy"]
  min_items: 1
  unique_items: true
```

## Common Parameter Schemas

The `CommonParameters` class provides pre-built schemas for common crystallography parameters:

### File Path
```python
CommonParameters.file_path(description: str = "Path to input file") -> JSONSchema
```

**Usage:**
```yaml
input_file:
  type: "string"
  description: "Path to input file"
  pattern: "^[^<>:\"|?*]+$"  # Basic file path validation
```

### Unit Cell
```python
CommonParameters.unit_cell() -> JSONSchema
```

**Generated Schema:**
```yaml
unit_cell:
  type: "object"
  properties:
    a: {"type": "number", "minimum": 0, "description": "Unit cell length a (Å)"}
    b: {"type": "number", "minimum": 0, "description": "Unit cell length b (Å)"}
    c: {"type": "number", "minimum": 0, "description": "Unit cell length c (Å)"}
    alpha: {"type": "number", "minimum": 0, "maximum": 180, "description": "Unit cell angle α (degrees)"}
    beta: {"type": "number", "minimum": 0, "maximum": 180, "description": "Unit cell angle β (degrees)"}
    gamma: {"type": "number", "minimum": 0, "maximum": 180, "description": "Unit cell angle γ (degrees)"}
  required: ["a", "b", "c", "alpha", "beta", "gamma"]
```

### Resolution Range
```python
CommonParameters.resolution_range() -> JSONSchema
```

**Generated Schema:**
```yaml
resolution_range:
  type: "object"
  properties:
    min: {"type": "number", "minimum": 0, "description": "Minimum resolution (Å)"}
    max: {"type": "number", "minimum": 0, "description": "Maximum resolution (Å)"}
  required: ["min", "max"]
```

### Space Group
```python
CommonParameters.space_group() -> JSONSchema
```

**Generated Schema:**
```yaml
space_group:
  type: "string"
  description: "Space group symbol or number"
  examples: ["P1", "P21", "P212121", "F432", "225"]
```

### Output Format
```python
CommonParameters.output_format(formats: List[str] = None) -> JSONSchema
```

**Generated Schema:**
```yaml
output_format:
  type: "string"
  enum: ["json", "csv", "text", "yaml"]
  default: "json"
  description: "Output format for results"
```

## Crystallography Schema Components

The `CrystallographySchema` class provides specialized schema components:

```python
class CrystallographySchema(BaseModel):
    unit_cell: Optional[JSONSchema]              # Unit cell parameters
    space_group: Optional[JSONSchema]            # Space group information
    resolution_range: Optional[JSONSchema]       # Resolution range
    file_input: Optional[JSONSchema]             # File input parameters
    quality_metrics: Optional[JSONSchema]        # Data quality metrics
    atomic_coordinates: Optional[JSONSchema]     # Atomic coordinate data
    reflection_data: Optional[JSONSchema]        # Reflection data
```

## Tool Configuration Types

### ToolConfiguration
Complete tool configuration with all available options:

```python
class ToolConfiguration(BaseModel):
    # Required fields
    module: str                                  # Python module path
    function: str                                # Function/class name
    description: str                             # Tool description
    
    # Optional fields
    auto_schema: bool = False                    # Auto-detect schemas
    file_input: bool = False                     # Handle file inputs
    input_schema: Optional[Union[JSONSchema, CrystallographySchema]]
    output_schema: Optional[Union[JSONSchema, CrystallographySchema]]
    
    # Tool-specific configuration
    tool_type: Optional[str]                     # Tool category
    dependencies: Optional[List[str]]            # Required packages
    timeout: Optional[int]                       # Execution timeout
    memory_limit: Optional[str]                  # Memory limit
    environment: Optional[Dict[str, str]]        # Environment variables
    
    # Metadata
    version: Optional[str]                       # Tool version
    author: Optional[str]                        # Tool author
    tags: Optional[List[str]]                    # Categorization tags
```

### ToolRegistryConfiguration
Complete registry configuration:

```python
class ToolRegistryConfiguration(BaseModel):
    version: str                                 # Configuration version
    description: Optional[str]                   # Collection description
    tools: Dict[str, ToolConfiguration]          # Tool definitions
    auto_reload: bool = False                    # Auto-reload tools
    default_format: Optional[str]                # Default output format
```

## Usage Examples

### Basic Tool with Auto-Schema
```yaml
my_tool:
  module: "my_package.tools"
  function: "MyTool"
  description: "A simple tool with automatic schema detection"
  auto_schema: true
  file_input: true
```

### Tool with Custom Schema
```yaml
advanced_tool:
  module: "my_package.advanced"
  function: "AdvancedTool"
  description: "Tool with custom validation rules"
  auto_schema: false
  input_schema:
    type: "object"
    properties:
      input_file:
        type: "string"
        description: "Path to input file"
        pattern: "^[^<>:\"|?*]+$"
      tolerance:
        type: "number"
        minimum: 0.001
        maximum: 10.0
        default: 0.1
    required: ["input_file"]
```

### Tool with Crystallography-Specific Types
```yaml
crystal_tool:
  module: "my_package.crystal"
  function: "CrystalTool"
  description: "Crystallography-specific tool"
  auto_schema: false
  input_schema:
    type: "object"
    properties:
      crystal_system:
        type: "string"
        enum: ["triclinic", "monoclinic", "orthorhombic", "tetragonal", "trigonal", "hexagonal", "cubic"]
      file_format:
        type: "string"
        enum: ["cif", "pdb", "mtz"]
    required: ["crystal_system", "file_format"]
```

## Best Practices

### 1. Use Enums for Constrained Values
```yaml
# Good
crystal_system:
  type: "string"
  enum: ["triclinic", "monoclinic", "orthorhombic", "tetragonal", "trigonal", "hexagonal", "cubic"]

# Avoid
crystal_system:
  type: "string"
  description: "Crystal system (triclinic, monoclinic, etc.)"
```

### 2. Provide Meaningful Constraints
```yaml
# Good
tolerance:
  type: "number"
  minimum: 0.001
  maximum: 10.0
  default: 0.1
  description: "Tolerance for parameter comparison (degrees/Å)"

# Avoid
tolerance:
  type: "number"
  description: "Tolerance value"
```

### 3. Use Common Parameter Schemas
```yaml
# Good - reuse common schemas
unit_cell: CommonParameters.unit_cell()

# Avoid - redefine common patterns
unit_cell:
  type: "object"
  properties:
    a: {"type": "number", "minimum": 0}
    # ... repeat for all parameters
```

### 4. Validate File Paths
```yaml
# Good
input_file:
  type: "string"
  pattern: "^[^<>:\"|?*]+$"
  description: "Path to input file"

# Avoid
input_file:
  type: "string"
  description: "Input file path"
```

### 5. Use Conditional Validation
```yaml
# Good - conditional requirements
if:
  properties:
    data_type: {"const": "file"}
then:
  required: ["file_path"]
else:
  required: ["content"]
```

## Reference

- **Models**: `src/xtalmcp/registry/models.py`
- **Templates**: `src/xtalmcp/registry/templates/`
- **Validation**: `src/xtalmcp/registry/validator.py`
- **CLI Commands**: `xtalmcp validate-yaml --help`

For more examples and advanced usage, see the template files and main documentation. 