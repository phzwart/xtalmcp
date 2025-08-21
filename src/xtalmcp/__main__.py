"""Command-line interface for XtalMCP server and tools."""
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

import click
from click import Context

from xtalmcp.server import create_server
from xtalmcp.tools import HelloTool
from xtalmcp.registry import YAMLToolRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool, quiet: bool) -> None:
    """Setup logging based on verbosity flags."""
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress all logging output')
@click.pass_context
def cli(ctx: Context, verbose: bool, quiet: bool) -> None:
    """XtalMCP - A minimal FastMCP server for crystallography tools."""
    setup_logging(verbose, quiet)
    ctx.ensure_object(dict)


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=8080, type=int, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
@click.option('--config', '-c', help='Path to YAML configuration file for tools')
def serve(host: str, port: int, reload: bool, config: Optional[str]) -> None:
    """Start the XtalMCP server."""
    try:
        server = create_server()
        
        # Register default tools
        server.register_tool_class(HelloTool)
        
        # Load tools from YAML if specified
        if config:
            from xtalmcp.registry import YAMLToolRegistry
            registry = YAMLToolRegistry(config)
            
            # Register all tools from the registry
            for tool_name, tool_instance in registry.tools.items():
                server.register_tool(tool_instance)
                click.echo(f"Registered YAML tool: {tool_name}")
        
        click.echo(f"Starting XtalMCP server on {host}:{port}")
        click.echo(f"Registered tools: {', '.join(server.list_tools())}")
        click.echo(f"Server URL: http://{host}:{port}")
        click.echo("Press Ctrl+C to stop the server")
        
        if reload:
            click.echo("Auto-reload enabled (development mode)")
            # Note: uvicorn reload requires running as module, not as script
            import uvicorn
            uvicorn.run(
                "xtalmcp.server:create_server().app",
                host=host,
                port=port,
                reload=True,
                log_level="info"
            )
        else:
            server.run(host=host, port=port)
            
    except KeyboardInterrupt:
        click.echo("\nServer stopped by user")
    except Exception as e:
        click.echo(f"Error starting server: {e}", err=True)
        raise click.Abort()


@cli.command()
def list_tools() -> None:
    """List all available tools."""
    try:
        # Create tool directly without server registration
        tool = HelloTool()
        
        click.echo("Available tools:")
        click.echo(f"  {tool.name}: {tool.description}")
            
    except Exception as e:
        click.echo(f"Error listing tools: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('tool_name')
@click.option('--file-path', '-f', help='Path to input file')
@click.option('--content', '-c', help='Direct input content')
@click.option('--output', '-o', help='Output file path (default: stdout)')
@click.option('--format', 'output_format', default='json', 
              type=click.Choice(['json', 'yaml', 'text']), 
              help='Output format')
@click.option('--name', help='Name parameter for hello_tool')
@click.option('--language', help='Language parameter for hello_tool')
def run_tool(tool_name: str, file_path: Optional[str], content: Optional[str], 
             output: Optional[str], output_format: str, name: Optional[str], language: Optional[str]) -> None:
    """Run a specific tool with given parameters."""
    try:
        # For now, only support hello_tool
        if tool_name != "hello_tool":
            click.echo(f"Tool '{tool_name}' not found. Available tools: hello_tool", err=True)
            raise click.Abort()
        
        tool = HelloTool()
        
        # Prepare parameters
        params = {}
        if file_path:
            params['file_path'] = file_path
        if content:
            params['content'] = content
        if name:
            params['name'] = name
        if language:
            params['language'] = language
        
        # Run tool
        click.echo(f"Running tool: {tool_name}")
        result = asyncio.run(tool.run(**params))
        
        # Format and output result
        if output_format == 'json':
            output_text = json.dumps(result, indent=2)
        elif output_format == 'yaml':
            try:
                import yaml
                output_text = yaml.dump(result, default_flow_style=False)
            except ImportError:
                click.echo("YAML output requires PyYAML. Falling back to JSON.", err=True)
                output_text = json.dumps(result, indent=2)
        else:  # text format
            output_text = str(result)
        
        if output:
            Path(output).write_text(output_text)
            click.echo(f"Output written to: {output}")
        else:
            click.echo(output_text)
            
    except Exception as e:
        click.echo(f"Error running tool: {e}", err=True)
        raise click.Abort()


@cli.command()
def version() -> None:
    """Show version information."""
    click.echo("XtalMCP version 1.0.0")


@cli.command()
def info() -> None:
    """Show server and tool information."""
    try:
        tool = HelloTool()
        
        click.echo("XtalMCP Server Information")
        click.echo("=" * 30)
        click.echo("Server Name: xtalmcp-server")
        click.echo("Version: 1.0.0")
        click.echo("Registered Tools: 1")
        click.echo()
        
        click.echo("Available Tools:")
        click.echo(f"  {tool.name}")
        click.echo(f"    Description: {tool.description}")
        if hasattr(tool, 'input_schema'):
            click.echo(f"    Input Schema: Available")
        click.echo()
            
    except Exception as e:
        click.echo(f"Error getting info: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--config', '-c', default='src/xtalmcp/registry/configs/default_tools.yaml',
              help='Path to YAML configuration file')
def load_yaml(config: str) -> None:
    """Load tools from YAML configuration file."""
    try:
        registry = YAMLToolRegistry(config)
        
        tools = registry.list_tools()
        if not tools:
            click.echo("No tools loaded from YAML configuration")
            return
        
        click.echo(f"Loaded {len(tools)} tools from {config}:")
        for tool_name in tools:
            tool = registry.get_tool(tool_name)
            click.echo(f"  {tool_name}: {tool.description}")
            
    except Exception as e:
        click.echo(f"Error loading YAML tools: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option('--config', '-c', required=True, help='Path to YAML configuration file to validate')
def validate_yaml(config: str) -> None:
    """Validate a YAML configuration file."""
    try:
        from xtalmcp.registry import validate_yaml_file
        
        # Validate the configuration
        validated_config = validate_yaml_file(config)
        
        click.echo(f"✅ Configuration file '{config}' is valid!")
        click.echo(f"   Version: {validated_config.version}")
        click.echo(f"   Description: {validated_config.description or 'No description'}")
        click.echo(f"   Tools: {len(validated_config.tools)}")
        
        # Show tool details
        for tool_name, tool_config in validated_config.tools.items():
            click.echo(f"   - {tool_name}: {tool_config.description}")
            if tool_config.auto_schema:
                click.echo(f"     (Auto-schema enabled)")
            if tool_config.file_input:
                click.echo(f"     (File input enabled)")
                
    except Exception as e:
        click.echo(f"❌ Configuration validation failed: {e}", err=True)
        raise click.Abort()


@cli.command()
def config_help() -> None:
    """Show help for YAML configuration format."""
    from xtalmcp.registry import print_configuration_help
    print_configuration_help()


@cli.command()
@click.option('--config', '-c', required=True, help='Path to YAML configuration file')
@click.option('--tool', '-t', required=True, help='Name of the tool to show schema for')
def show_schema(config: str, tool: str) -> None:
    """Show the MCP JSON schema for a specific tool."""
    try:
        from xtalmcp.registry import YAMLToolRegistry
        
        # Load the registry
        registry = YAMLToolRegistry(config)
        
        # Get the tool
        tool_instance = registry.get_tool(tool)
        if not tool_instance:
            click.echo(f"❌ Tool '{tool}' not found in configuration", err=True)
            raise click.Abort()
        
        # Get the tool schema
        schema = tool_instance.get_tool_schema()
        
        click.echo(f"🔧 MCP JSON Schema for tool '{tool}':")
        click.echo("=" * 50)
        
        # Pretty print the schema
        import json
        
        # Clean the schema for JSON serialization
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif hasattr(obj, '__name__'):  # Handle function/class objects
                return str(obj)
            elif hasattr(obj, 'dtype'):  # Handle numpy types
                return str(obj)
            else:
                try:
                    json.dumps(obj)
                    return obj
                except (TypeError, ValueError):
                    return str(obj)
        
        cleaned_schema = clean_for_json(schema)
        click.echo(json.dumps(cleaned_schema, indent=2))
        
    except Exception as e:
        click.echo(f"❌ Error showing schema: {e}", err=True)
        raise click.Abort()


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()  # pragma: no cover
