# YAML Configuration Guide

This guide explains how to create and validate YAML configuration files for XtalMCP tools.

## Overview

XtalMCP uses YAML configuration files to define tools that can be dynamically loaded into the system. This approach provides:

- **Zero-code integration**: Add tools without modifying the core system
- **Declarative configuration**: Define tool behavior in YAML
- **Automatic validation**: Built-in schema validation ensures correctness
- **Flexible schemas**: Choose between auto-detection and custom schemas

## Quick Start

### 1. Copy the Template

Start with the provided template:

```bash
cp src/xtalmcp/registry/templates/tool_config_template.yaml my_tools.yaml
```

### 2. Modify for Your Tools

Edit the template to define your tools. See the instruction set below for all available options.

### 3. Validate Your Configuration

```bash
xtalmcp validate-yaml --config my_tools.yaml
```

### 4. Load Your Tools

```bash
xtalmcp load-yaml --config my_tools.yaml
```

## Configuration Structure

### Root Level Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `version` | string | Yes | - | Configuration file version |
| `description` | string | No | - | Overall description of tool collection |
| `tools` | object | Yes | - | Dictionary of tool configurations |
| `auto_reload` | boolean | No | false | Auto-reload tools when files change |
| `default_format` | string | No | - | Default output format for tools |

### Tool Configuration Fields

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `module` | string | Python module path (e.g., "my_package.tools") |
| `function` | string | Function or class name within the module |
| `description` | string | Human-readable description of the tool |

#### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `auto_schema` | boolean | false | Auto-detect schemas from type hints |
| `file_input` | boolean | false | Tool handles file inputs |
| `input_schema` | object | - | Custom input schema definition |
| `output_schema` | object | - | Custom output schema definition |
| `version` | string | - | Tool version string |
| `author` | string | - | Tool author/maintainer |
| `tags` | array | - | List of tags for categorization |

## Schema Options

### Auto-Schema Detection

When `auto_schema: true`, XtalMCP automatically generates JSON schemas from your Python function's type hints.

**Requirements for auto-schema:**
- Function must have type hints
- Function must have a docstring (first line becomes description)
- No custom schemas can be provided

### Custom Schema Definition

When `auto_schema: false`, you can define custom schemas. See the Type Definitions Reference for complete schema options.

## File Input Handling

When `file_input: true`, your tool can accept both file paths and direct content.

**Benefits of file_input: true:**
- Tool can accept `file_path` parameter
- Tool can accept `content` parameter
- Automatic file reading and content extraction
- Fallback handling for different input types

## Configuration Instructions

### Required Fields

Every tool must have these three fields:

- **`module`**: Python module path (e.g., "my_package.tools")
- **`function`**: Function or class name within the module
- **`description`**: Human-readable description of the tool

### Optional Fields

Additional configuration options:

- **`auto_schema`**: Whether to auto-detect schemas (default: false)
- **`file_input`**: Whether tool handles file inputs (default: false)
- **`input_schema`**: Custom input schema definition
- **`output_schema`**: Custom output schema definition
- **`version`**: Tool version string
- **`author`**: Tool author/maintainer
- **`tags`**: List of tags for categorization
- **`tool_type`**: Tool category (e.g., "data_processing", "validation")
- **`dependencies`**: List of required Python packages
- **`timeout`**: Execution timeout in seconds
- **`memory_limit`**: Memory limit (e.g., "1GB", "512MB")
- **`environment`**: Environment variables for execution

### Global Settings

Configuration file options:

- **`version`**: Configuration file version
- **`description`**: Overall description of tool collection
- **`auto_reload`**: Automatically reload tools when files change
- **`default_format`**: Default output format for tools

### Schema Validation Rules

- All schemas follow JSON Schema specification
- Use "required" array to specify mandatory parameters
- Use "enum" to restrict values to specific options
- Use "default" to provide default values
- Use "minimum"/"maximum" for numeric constraints
- Use "pattern" for string validation (e.g., file paths)
- Use "one_of" for conditional validation
- Use "if"/"then"/"else" for complex validation logic

## CLI Commands

### Validate Configuration

```bash
# Validate a specific configuration file
xtalmcp validate-yaml --config my_tools.yaml

# Output example:
✅ Configuration file 'my_tools.yaml' is valid!
   Version: 1.0
   Description: My Crystallography Tools
   Tools: 2
   - my_tool: Process crystallography data
     (Auto-schema enabled)
   - plot_tool: Generate plots
     (File input enabled)
```

### Get Configuration Help

```bash
# Show configuration format help
xtalmcp config-help

# Output shows required fields, optional fields, and examples
```

### Load Tools

```bash
# Load tools from configuration
xtalmcp load-yaml --config my_tools.yaml

# Load from default configuration
xtalmcp load-yaml
```

## Best Practices

### 1. Use Descriptive Names
- Choose clear, descriptive tool names that indicate their purpose
- Use underscores to separate words (e.g., `extract_unit_cell_parameters`)

### 2. Provide Meaningful Descriptions
- Write clear descriptions that explain what the tool does
- Include key parameters or file types the tool processes

### 3. Use Tags for Organization
- Add relevant tags to categorize your tools
- Use consistent tag naming conventions

### 4. Version Your Tools
- Include version numbers for tracking changes
- Add author information for attribution

### 5. Test Your Configuration
- Always validate before loading: `xtalmcp validate-yaml --config my_tools.yaml`
- Check for validation errors and fix them before deployment

## Troubleshooting

### Common Validation Errors

1. **Missing Required Fields**
   - Ensure `module`, `function`, and `description` are present

2. **Schema Conflicts**
   - Set `auto_schema: false` when providing custom schemas

3. **Invalid Module Paths**
   - Use dot notation: `package.submodule`
   - Avoid single words: `module` (invalid)

4. **Invalid Function Names**
   - Use alphanumeric characters and underscores only
   - Avoid special characters or spaces

### Getting Help

- Use `xtalmcp config-help` for format information
- Check the template file for examples
- Validate your configuration before loading
- Review error messages for specific validation failures

## Advanced Usage

### Conditional Tool Loading
- Use environment variables or conditions to control tool loading
- Implement development vs. production tool configurations

### Tool Dependencies
- Document required Python packages in the `dependencies` field
- Use tags to indicate external tool requirements

### Custom Validation
- Use custom schemas for complex validation rules
- Implement conditional validation with `if`/`then`/`else`
- Use `one_of` for mutually exclusive parameter sets

## Reference

- **Template File**: `src/xtalmcp/registry/templates/tool_config_template.yaml`
- **Schema Models**: `src/xtalmcp/registry/models.py`
- **Validation Functions**: `src/xtalmcp/registry/validator.py`
- **CLI Commands**: `xtalmcp --help`

For more information, see the main XtalMCP documentation and examples. 