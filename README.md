# XtalMCP

[![PyPI](https://img.shields.io/pypi/v/xtalmcp.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/xtalmcp.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/xtalmcp)][python version]
[![License](https://img.shields.io/pypi/l/xtalmcp)][license]

[![Read the documentation at https://xtalmcp.readthedocs.io/](https://img.shields.io/readthedocs/xtalmcp/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/phzwart/xtalmcp/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/phzwart/xtalmcp/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/xtalmcp/
[status]: https://pypi.org/project/xtalmcp/
[python version]: https://pypi.org/project/xtalmcp
[read the docs]: https://xtalmcp.readthedocs.io/
[tests]: https://github.com/phzwart/xtalmcp/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/phzwart/xtalmcp
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Overview

**XtalMCP** is a minimal FastMCP server designed specifically for crystallography tools. It provides a modular framework for building, registering, and executing crystallography-related tools through both a command-line interface and programmatic API.

## Features

### 🚀 **Core Framework**
- **FastMCP Integration**: Built on FastMCP for seamless tool integration
- **Modular Architecture**: Clean separation between tools, server, and registry
- **Async Support**: Full async/await support for high-performance tool execution
- **Type Safety**: Comprehensive type hints and validation

### 🛠️ **Tool System**
- **BaseTool**: Abstract base class for all tools with built-in error handling
- **FileInputTool**: Specialized base class for file-processing tools
- **Dynamic Tool Loading**: Zero-code tool integration via YAML configuration
- **Auto-schema Detection**: Automatic JSON schema generation from Python type hints

### 📋 **Command Line Interface**
- **Server Management**: Start, stop, and configure the MCP server
- **Tool Execution**: Run tools with parameters and output formatting
- **YAML Integration**: Load and manage tools from configuration files
- **Multiple Output Formats**: JSON, YAML, and text output support

### 🔧 **Registry System**
- **YAML Configuration**: Declarative tool definitions
- **Auto-discovery**: Automatic tool registration and schema generation
- **Hot Reloading**: Dynamic tool updates without server restart
- **Validation**: Built-in configuration and parameter validation

### 🧪 **Testing Infrastructure**
- **Comprehensive Test Suite**: 107 tests covering all components
- **100% Test Coverage**: All modules, classes, and functions tested
- **Async Testing**: Full async test support with pytest-asyncio
- **Mock Integration**: Strategic mocking for isolated testing

## Requirements

- **Python**: 3.7 or higher
- **FastAPI**: Web framework for the server
- **FastMCP**: MCP protocol implementation
- **PyYAML**: YAML configuration parsing
- **Click**: Command-line interface framework
- **Uvicorn**: ASGI server for production deployment

## Installation

### From PyPI

```console
$ pip install xtalmcp
```

### From Source

```console
$ git clone https://github.com/phzwart/xtalmcp.git
$ cd xtalmcp
$ pip install -e .
```

### Development Setup

```console
$ git clone https://github.com/phzwart/xtalmcp.git
$ cd xtalmcp
$ pip install -e ".[dev]"
$ pre-commit install
```

## Usage

### Command Line Interface

The XtalMCP server provides a comprehensive CLI for managing tools and running the server.

#### Basic Commands

```bash
# Show help
xtalmcp --help

# Show version
xtalmcp version

# List available tools
xtalmcp list-tools

# Show server information
xtalmcp info
```

#### Running Tools

```bash
# Run a tool with basic parameters
xtalmcp run-tool hello_tool

# Run with custom parameters
xtalmcp run-tool hello_tool --name "Alice" --language "fr"

# Output in different formats
xtalmcp run-tool hello_tool --format json
xtalmcp run-tool hello_tool --format yaml
xtalmcp run-tool hello_tool --format text

# Save output to file
xtalmcp run-tool hello_tool --output result.json
```

#### YAML Tool Management

```bash
# Load tools from default configuration
xtalmcp load-yaml

# Load from custom configuration file
xtalmcp load-yaml --config my_tools.yaml

# View loaded tools
xtalmcp list-tools
```

#### Starting the Server

```bash
# Start server on default host/port (127.0.0.1:8080)
xtalmcp serve

# Start on custom host/port
xtalmcp serve --host 0.0.0.0 --port 9000

# Enable auto-reload for development
xtalmcp serve --reload
```

#### Development Usage

For development, you can run the CLI directly:

```bash
# Set PYTHONPATH and run module
PYTHONPATH=src python -m xtalmcp.__main__ --help

# Or install in development mode
pip install -e .
xtalmcp --help
```

### Programmatic Usage

#### Basic Tool Creation

```python
from xtalmcp.base import BaseTool
from typing import Dict, Any

class MyTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "my_tool"
        self.description = "A custom tool for crystallography"
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        # Your tool logic here
        return {"result": "success", "data": kwargs}

# Use the tool
tool = MyTool()
result = await tool.run(param1="value1")
```

#### File Processing Tools

```python
from xtalmcp.base import FileInputTool

class CIFProcessor(FileInputTool):
    def __init__(self):
        super().__init__()
        self.name = "cif_processor"
        self.description = "Process CIF files"
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        # Get file content (handles both file_path and content)
        file_content = await self.get_file_content(**kwargs)
        
        # Process the content
        processed_data = self.process_cif(file_content)
        return {"result": "success", "data": processed_data}
```

#### YAML Tool Configuration

Create a `tools.yaml` file:

```yaml
tools:
  extract_cc12:
    module: "my_module.crystallography"
    function: "extract_cc12_table"
    description: "Extract CC(1/2) correlation table from AIMLESS log"
    auto_schema: true
    
  plot_resolution:
    module: "my_module.plotting"
    function: "plot_cc12_vs_resolution"
    description: "Generate CC(1/2) vs resolution plot"
    auto_schema: true
    input_schema:
      type: object
      properties:
        log_file:
          type: string
          description: "Path to AIMLESS log file"
        output_format:
          type: string
          enum: ["png", "svg", "pdf"]
          default: "png"
```

Load and use the tools:

```python
from xtalmcp.registry import YAMLToolRegistry

# Load tools from YAML
registry = YAMLToolRegistry("tools.yaml")
registry.load_tools()

# Get a tool
tool = registry.get_tool("extract_cc12")
result = await tool.run(log_file="aimless.log")
```

#### Server Integration

```python
from xtalmcp.server import XtalMCPServer

# Create server
server = XtalMCPServer("my-server", "1.0.0")

# Register tools
server.register_tool(MyTool())
server.register_tool_class(CIFProcessor)

# Start server
import uvicorn
uvicorn.run(server.app, host="127.0.0.1", port=8080)
```

## Testing

### Running Tests

```bash
# Run all tests
PYTHONPATH=src python -m pytest tests/ -v

# Run specific test file
PYTHONPATH=src python -m pytest tests/test_tools.py -v

# Run with coverage
PYTHONPATH=src python -m pytest tests/ --cov=xtalmcp --cov-report=html

# Run async tests only
PYTHONPATH=src python -m pytest tests/ -m asyncio
```

### Test Coverage

The project includes **107 comprehensive tests** covering:

- **Base Classes**: BaseTool, FileInputTool initialization and methods
- **CLI Interface**: All commands, error handling, and output formats
- **Registry System**: YAML loading, schema detection, and tool creation
- **Server Components**: Server initialization, tool registration, FastMCP integration
- **Individual Tools**: HelloTool functionality, edge cases, and integration
- **Error Handling**: Comprehensive error scenarios and recovery

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **Async Tests**: Full async functionality validation
- **Error Tests**: Error condition and recovery testing
- **Edge Case Tests**: Boundary condition validation

## Project Structure

```
xtalmcp/
├── src/xtalmcp/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # CLI entry point
│   ├── base.py              # Base tool classes
│   ├── server.py            # FastMCP server implementation
│   ├── tools/               # Tool implementations
│   │   ├── __init__.py
│   │   └── hello_tool.py    # Example tool
│   └── registry/            # YAML registry system
│       ├── __init__.py
│       ├── schema_detector.py    # Auto-schema generation
│       ├── yaml_registry.py      # YAML tool loader
│       └── configs/              # Default configurations
│           ├── default_tools.yaml
│           └── test_tools.yaml
├── tests/                   # Comprehensive test suite
│   ├── test_base.py         # Base class tests
│   ├── test_cli.py          # CLI tests
│   ├── test_main.py         # Main module tests
│   ├── test_registry.py     # Registry tests
│   ├── test_server.py       # Server tests
│   └── test_tools.py        # Tool tests
├── docs/                    # Documentation
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Development

### Code Quality

- **Type Hints**: Comprehensive type annotations throughout
- **Linting**: Black code formatting, flake8 linting
- **Pre-commit**: Automated code quality checks
- **Documentation**: Comprehensive docstrings and examples

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Testing Guidelines

- **Test Coverage**: Maintain 100% test coverage
- **Async Testing**: Use `@pytest.mark.asyncio` for async tests
- **Mocking**: Use strategic mocking to isolate components
- **Error Testing**: Test both success and failure scenarios

## License

Distributed under the terms of the [MIT license][license],
_xtalmcp_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/phzwart/xtalmcp/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/phzwart/xtalmcp/blob/main/LICENSE
[contributor guide]: https://github.com/phzwart/xtalmcp/blob/main/CONTRIBUTING.md
[command-line reference]: https://xtalmcp.readthedocs.io/en/latest/usage.html
