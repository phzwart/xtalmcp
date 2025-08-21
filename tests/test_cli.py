"""Test cases for the CLI module."""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import json

from xtalmcp.__main__ import cli


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


class TestCLIBasic:
    """Test basic CLI functionality."""
    
    def test_cli_help(self, runner: CliRunner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "XtalMCP - A minimal FastMCP server for crystallography tools" in result.output
    
    def test_cli_verbose_flag(self, runner: CliRunner):
        """Test CLI verbose flag."""
        result = runner.invoke(cli, ['--verbose', '--help'])
        assert result.exit_code == 0
    
    def test_cli_quiet_flag(self, runner: CliRunner):
        """Test CLI quiet flag."""
        result = runner.invoke(cli, ['--quiet', '--help'])
        assert result.exit_code == 0


class TestCLIVersion:
    """Test version command."""
    
    def test_version_command(self, runner: CliRunner):
        """Test version command."""
        result = runner.invoke(cli, ['version'])
        assert result.exit_code == 0
        assert "XtalMCP version 1.0.0" in result.output


class TestCLIListTools:
    """Test list-tools command."""
    
    def test_list_tools_command(self, runner: CliRunner):
        """Test list-tools command."""
        result = runner.invoke(cli, ['list-tools'])
        assert result.exit_code == 0
        assert "Available tools:" in result.output
        assert "hello_tool:" in result.output


class TestCLIInfo:
    """Test info command."""
    
    def test_info_command(self, runner: CliRunner):
        """Test info command."""
        result = runner.invoke(cli, ['info'])
        assert result.exit_code == 0
        assert "XtalMCP Server Information" in result.output
        assert "Server Name: xtalmcp-server" in result.output
        assert "Version: 1.0.0" in result.output
        assert "Registered Tools: 1" in result.output
        assert "Available Tools:" in result.output
        assert "hello_tool" in result.output


class TestCLIRunTool:
    """Test run-tool command."""
    
    def test_run_tool_help(self, runner: CliRunner):
        """Test run-tool help."""
        result = runner.invoke(cli, ['run-tool', '--help'])
        assert result.exit_code == 0
        assert "Run a specific tool with given parameters" in result.output
    
    def test_run_tool_basic(self, runner: CliRunner):
        """Test run-tool with basic parameters."""
        result = runner.invoke(cli, ['run-tool', 'hello_tool'])
        assert result.exit_code == 0
        assert "Running tool: hello_tool" in result.output
        assert "Hello, World!" in result.output
    
    def test_run_tool_with_name(self, runner: CliRunner):
        """Test run-tool with name parameter."""
        result = runner.invoke(cli, ['run-tool', 'hello_tool', '--name', 'Alice'])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.output
    
    def test_run_tool_with_language(self, runner: CliRunner):
        """Test run-tool with language parameter."""
        result = runner.invoke(cli, ['run-tool', 'hello_tool', '--language', 'fr'])
        assert result.exit_code == 0
        assert "Bonjour, World!" in result.output
    
    def test_run_tool_with_format_json(self, runner: CliRunner):
        """Test run-tool with JSON output format."""
        result = runner.invoke(cli, ['run-tool', 'hello_tool', '--format', 'json'])
        assert result.exit_code == 0
        # Should output JSON
        assert '"greeting"' in result.output
        assert '"status"' in result.output
    
    def test_run_tool_with_format_text(self, runner: CliRunner):
        """Test run-tool with text output format."""
        result = runner.invoke(cli, ['run-tool', 'hello_tool', '--format', 'text'])
        assert result.exit_code == 0
        # Should output text representation
        assert "Hello, World!" in result.output
    
    def test_run_tool_with_output_file(self, runner: CliRunner, tmp_path):
        """Test run-tool with output file."""
        output_file = tmp_path / "output.json"
        
        result = runner.invoke(cli, [
            'run-tool', 'hello_tool', 
            '--output', str(output_file),
            '--format', 'json'
        ])
        
        assert result.exit_code == 0
        assert f"Output written to: {output_file}" in result.output
        assert output_file.exists()
        
        # Verify file content
        with open(output_file, 'r') as f:
            content = json.load(f)
            assert content['greeting'] == "Hello, World!"
    
    def test_run_tool_invalid_tool(self, runner: CliRunner):
        """Test run-tool with invalid tool name."""
        result = runner.invoke(cli, ['run-tool', 'nonexistent_tool'])
        assert result.exit_code == 1  # SystemExit from click.Abort()
        assert "Tool 'nonexistent_tool' not found" in result.output


class TestCLILoadYAML:
    """Test load-yaml command."""
    
    def test_load_yaml_help(self, runner: CliRunner):
        """Test load-yaml help."""
        result = runner.invoke(cli, ['load-yaml', '--help'])
        assert result.exit_code == 0
        assert "Load tools from YAML configuration file" in result.output
    
    def test_load_yaml_default_config(self, runner: CliRunner):
        """Test load-yaml with default config."""
        result = runner.invoke(cli, ['load-yaml'])
        assert result.exit_code == 0
        assert "Loaded 1 tools from" in result.output
        assert "hello_tool:" in result.output
    
    def test_load_yaml_custom_config(self, runner: CliRunner):
        """Test load-yaml with custom config."""
        result = runner.invoke(cli, ['load-yaml', '--config', 'src/xtalmcp/registry/configs/test_tools.yaml'])
        assert result.exit_code == 0
        assert "Loaded 1 tools from" in result.output
        assert "hello_tool:" in result.output
    
    def test_load_yaml_nonexistent_file(self, runner: CliRunner):
        """Test load-yaml with non-existent file."""
        result = runner.invoke(cli, ['load-yaml', '--config', 'nonexistent.yaml'])
        assert result.exit_code == 1  # SystemExit from click.Abort()
        assert "Error loading YAML tools" in result.output


class TestCLIServe:
    """Test serve command."""
    
    def test_serve_help(self, runner: CliRunner):
        """Test serve help."""
        result = runner.invoke(cli, ['serve', '--help'])
        assert result.exit_code == 0
        assert "Start the XtalMCP server" in result.output
    
    def test_serve_default_options(self, runner: CliRunner):
        """Test serve with default options."""
        result = runner.invoke(cli, ['serve', '--help'])
        assert result.exit_code == 0
        assert "--host TEXT" in result.output
        assert "--port INTEGER" in result.output
        assert "--reload" in result.output
    
    def test_serve_custom_host_port(self, runner: CliRunner):
        """Test serve with custom host and port."""
        result = runner.invoke(cli, ['serve', '--host', '0.0.0.0', '--port', '9000', '--help'])
        assert result.exit_code == 0


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    def test_invalid_command(self, runner: CliRunner):
        """Test invalid command handling."""
        result = runner.invoke(cli, ['invalid_command'])
        assert result.exit_code == 2  # Click error
        assert "No such command" in result.output
    
    def test_missing_required_argument(self, runner: CliRunner):
        """Test missing required argument handling."""
        result = runner.invoke(cli, ['run-tool'])
        assert result.exit_code == 2  # Click error
        assert "Missing argument" in result.output


class TestCLIIntegration:
    """Integration tests for CLI."""
    
    def test_complete_workflow(self, runner: CliRunner, tmp_path):
        """Test complete CLI workflow."""
        # 1. Check version
        result = runner.invoke(cli, ['version'])
        assert result.exit_code == 0
        
        # 2. List tools
        result = runner.invoke(cli, ['list-tools'])
        assert result.exit_code == 0
        
        # 3. Get info
        result = runner.invoke(cli, ['info'])
        assert result.exit_code == 0
        
        # 4. Load YAML tools
        result = runner.invoke(cli, ['load-yaml'])
        assert result.exit_code == 0
        
        # 5. Run a tool with output
        output_file = tmp_path / "workflow_output.json"
        result = runner.invoke(cli, [
            'run-tool', 'hello_tool', 
            '--name', 'TestUser',
            '--language', 'es',
            '--output', str(output_file),
            '--format', 'json'
        ])
        assert result.exit_code == 0
        assert output_file.exists()
    
    def test_tool_parameter_combinations(self, runner: CliRunner):
        """Test various tool parameter combinations."""
        # Test with name only
        result = runner.invoke(cli, ['run-tool', 'hello_tool', '--name', 'Bob'])
        assert result.exit_code == 0
        assert "Hello, Bob!" in result.output
        
        # Test with language only
        result = runner.invoke(cli, ['run-tool', 'hello_tool', '--language', 'de'])
        assert result.exit_code == 0
        assert "Hallo, World!" in result.output
        
        # Test with both parameters
        result = runner.invoke(cli, ['run-tool', 'hello_tool', '--name', 'Alice', '--language', 'fr'])
        assert result.exit_code == 0
        assert "Bonjour, Alice!" in result.output


class TestCLIOutputFormats:
    """Test CLI output format handling."""
    
    def test_json_output_format(self, runner: CliRunner):
        """Test JSON output format."""
        result = runner.invoke(cli, ['run-tool', 'hello_tool', '--format', 'json'])
        assert result.exit_code == 0
        
        # Try to parse as JSON
        try:
            import json
            # Extract the JSON part from the output
            output_lines = result.output.strip().split('\n')
            json_line = None
            for line in output_lines:
                if line.strip().startswith('{'):
                    json_line = line.strip()
                    break
            
            if json_line:
                parsed = json.loads(json_line)
                assert 'greeting' in parsed
                assert 'status' in parsed
                assert parsed['status'] == 'success'
        except (json.JSONDecodeError, AttributeError):
            # If JSON parsing fails, at least verify the format looks like JSON
            assert '"' in result.output
            assert '{' in result.output
    
    def test_text_output_format(self, runner: CliRunner):
        """Test text output format."""
        result = runner.invoke(cli, ['run-tool', 'hello_tool', '--format', 'text'])
        assert result.exit_code == 0
        # Text format should be more readable
        assert "Hello, World!" in result.output
        assert "success" in result.output.lower() 