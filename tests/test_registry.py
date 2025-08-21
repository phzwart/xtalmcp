"""Test cases for the registry package."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from typing import Dict, Any

from xtalmcp.registry import YAMLToolRegistry, SchemaDetector
from xtalmcp.registry.yaml_registry import DynamicTool


class TestSchemaDetector:
    """Test cases for SchemaDetector class."""
    
    def test_detect_schema_basic_function(self):
        """Test schema detection for a basic function."""
        def test_func(name: str, age: int = 25) -> str:
            """A test function with basic types."""
            return f"Hello {name}, age {age}"
        
        schema = SchemaDetector.detect_schema(test_func)
        
        assert schema['description'] == "A test function with basic types."
        assert 'input_schema' in schema
        assert 'output_schema' in schema
        
        input_schema = schema['input_schema']
        assert input_schema['type'] == 'object'
        assert 'name' in input_schema['properties']
        assert 'age' in input_schema['properties']
        assert input_schema['required'] == ['name']
        
        # Check parameter types
        assert input_schema['properties']['name']['type'] == 'string'
        assert input_schema['properties']['age']['type'] == 'integer'
        assert input_schema['properties']['age']['default'] == 25
    
    def test_detect_schema_complex_types(self):
        """Test schema detection for complex types."""
        def test_func(data: Dict[str, Any], items: list, optional: str = None) -> bool:
            """A test function with complex types."""
            return True
        
        schema = SchemaDetector.detect_schema(test_func)
        
        input_schema = schema['input_schema']
        assert input_schema['properties']['data']['type'] == 'object'
        assert input_schema['properties']['items']['type'] == 'array'
        assert input_schema['properties']['optional']['type'] == 'string'
        assert 'optional' not in input_schema['required']
    
    def test_detect_schema_optional_types(self):
        """Test schema detection for Optional types."""
        from typing import Optional
        
        def test_func(required: str, optional: Optional[int] = None) -> str:
            """A test function with Optional types."""
            return "test"
        
        schema = SchemaDetector.detect_schema(test_func)
        
        input_schema = schema['input_schema']
        assert input_schema['properties']['required']['type'] == 'string'
        assert input_schema['properties']['optional']['type'] == 'integer'
        assert 'required' in input_schema['required']
        assert 'optional' not in input_schema['required']
    
    def test_detect_schema_no_docstring(self):
        """Test schema detection for function without docstring."""
        def test_func(param: str) -> str:
            return param
        
        schema = SchemaDetector.detect_schema(test_func)
        
        assert schema['description'] == ""
        assert 'input_schema' in schema
        assert 'output_schema' in schema
    
    def test_detect_schema_method(self):
        """Test schema detection for class method."""
        class TestClass:
            def test_method(self, param: str) -> str:
                """A test method."""
                return param
        
        schema = SchemaDetector.detect_schema(TestClass.test_method)
        
        # Should skip 'self' parameter
        assert 'self' not in schema['input_schema']['properties']
        assert 'param' in schema['input_schema']['properties']


class TestDynamicTool:
    """Test cases for DynamicTool class."""
    
    def test_dynamic_tool_creation(self):
        """Test DynamicTool creation with basic config."""
        def test_func(param: str) -> str:
            return f"Hello {param}"
        
        config = {
            'description': 'Test tool',
            'input_schema': {'type': 'object', 'properties': {}},
            'output_schema': {'type': 'string'}
        }
        
        tool = DynamicTool('test_tool', test_func, config)
        
        assert tool.name == 'test_tool'
        assert tool.description == 'Test tool'
        assert tool.function == test_func
        assert tool.config == config
    
    @pytest.mark.asyncio
    async def test_dynamic_tool_execute_sync(self):
        """Test DynamicTool execution with sync function."""
        def test_func(name: str) -> str:
            return f"Hello {name}"
        
        config = {
            'description': 'Test tool',
            'input_schema': {'type': 'object', 'properties': {}},
            'output_schema': {'type': 'string'}
        }
        
        tool = DynamicTool('test_tool', test_func, config)
        
        result = await tool.execute(name="World")
        
        assert result['status'] == 'success'
        assert result['result'] == "Hello World"
        assert result['tool_name'] == 'test_tool'
    
    @pytest.mark.asyncio
    async def test_dynamic_tool_execute_async(self):
        """Test DynamicTool execution with async function."""
        async def test_func(name: str) -> str:
            return f"Hello {name}"
        
        config = {
            'description': 'Test tool',
            'input_schema': {'type': 'object', 'properties': {}},
            'output_schema': {'type': 'string'}
        }
        
        tool = DynamicTool('test_tool', test_func, config)
        
        result = await tool.execute(name="World")
        
        assert result['status'] == 'success'
        assert result['result'] == "Hello World"
    
    @pytest.mark.asyncio
    async def test_dynamic_tool_execute_error(self):
        """Test DynamicTool error handling."""
        def test_func(param: str) -> str:
            raise ValueError("Test error")
        
        config = {
            'description': 'Test tool',
            'input_schema': {'type': 'object', 'properties': {}},
            'output_schema': {'type': 'string'}
        }
        
        tool = DynamicTool('test_tool', test_func, config)
        
        result = await tool.execute(param="test")
        
        assert result['status'] == 'error'
        assert 'Test error' in result['error']
        assert result['tool_name'] == 'test_tool'
    
    def test_dynamic_tool_file_input(self):
        """Test DynamicTool with file input flag."""
        def test_func(file_path: str) -> str:
            return f"Processed {file_path}"
        
        config = {
            'description': 'File processing tool',
            'file_input': True,
            'input_schema': {'type': 'object', 'properties': {}},
            'output_schema': {'type': 'string'}
        }
        
        tool = DynamicTool('file_tool', test_func, config)
        
        assert tool.file_input is True
    
    def test_dynamic_tool_is_async_function(self):
        """Test async function detection."""
        def sync_func():
            pass
        
        async def async_func():
            pass
        
        tool = DynamicTool('test', sync_func, {})
        
        assert tool._is_async_function(sync_func) is False
        assert tool._is_async_function(async_func) is True


class TestYAMLToolRegistry:
    """Test cases for YAMLToolRegistry class."""
    
    def test_registry_initialization(self):
        """Test YAMLToolRegistry initialization."""
        registry = YAMLToolRegistry()
        
        assert registry.yaml_path is None
        assert registry.tools == {}
        assert registry.config == {}
    
    def test_registry_initialization_with_path(self):
        """Test YAMLToolRegistry initialization with YAML path."""
        with patch('builtins.open', mock_open(read_data='tools:\n  test: {}')):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('yaml.safe_load', return_value={'tools': {'test': {}}}):
                    registry = YAMLToolRegistry('test.yaml')
                    
                    assert registry.yaml_path == 'test.yaml'
    
    def test_load_tools_file_not_found(self):
        """Test loading tools from non-existent file."""
        registry = YAMLToolRegistry()
        
        with pytest.raises(FileNotFoundError):
            registry.load_tools('nonexistent.yaml')
    
    def test_load_tools_no_yaml_path(self):
        """Test loading tools without YAML path."""
        registry = YAMLToolRegistry()
        
        with pytest.raises(ValueError, match="No YAML path specified"):
            registry.load_tools()
    
    def test_load_tools_invalid_yaml(self):
        """Test loading tools from invalid YAML."""
        registry = YAMLToolRegistry()
        
        with patch('builtins.open', mock_open(read_data='invalid: yaml: content')):
            with patch('pathlib.Path.exists', return_value=True):
                with pytest.raises(Exception):  # yaml.YAMLError
                    registry.load_tools('test.yaml')
    
    def test_load_tools_no_tools_section(self):
        """Test loading YAML without tools section."""
        registry = YAMLToolRegistry()
        
        with patch('builtins.open', mock_open(read_data='other:\n  key: value')):
            with patch('pathlib.Path.exists', return_value=True):
                registry.load_tools('test.yaml')
                
                assert registry.tools == {}
    
    def test_create_tool_missing_required_fields(self):
        """Test tool creation with missing required fields."""
        registry = YAMLToolRegistry()
        
        config = {'description': 'Test tool'}  # Missing module and function
        
        with pytest.raises(ValueError, match="Missing required field"):
            registry._create_tool_from_config('test_tool', config)
    
    def test_create_tool_import_error(self):
        """Test tool creation with import error."""
        registry = YAMLToolRegistry()
        
        config = {
            'module': 'nonexistent_module',
            'function': 'test_function'
        }
        
        with pytest.raises(ValueError, match="Could not import"):
            registry._create_tool_from_config('test_tool', config)
    
    def test_create_tool_attribute_error(self):
        """Test tool creation with attribute error."""
        registry = YAMLToolRegistry()
        
        config = {
            'module': 'builtins',
            'function': 'nonexistent_function'
        }
        
        with pytest.raises(ValueError, match="Could not import"):
            registry._create_tool_from_config('test_tool', config)
    
    def test_create_tool_with_auto_schema(self):
        """Test tool creation with auto-schema detection."""
        registry = YAMLToolRegistry()
        
        def test_func(param: str) -> str:
            """Test function."""
            return param
        
        config = {
            'module': 'builtins',
            'function': 'str',
            'auto_schema': True
        }
        
        # Mock the import to return our test function
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_module.str = test_func
            mock_import.return_value = mock_module
            
            tool = registry._create_tool_from_config('test_tool', config)
            
            assert tool.name == 'test_tool'
            assert 'input_schema' in tool.config
            assert 'output_schema' in tool.config
    
    def test_get_tool(self):
        """Test getting tool by name."""
        registry = YAMLToolRegistry()
        
        # Mock tool
        mock_tool = Mock()
        registry.tools['test_tool'] = mock_tool
        
        assert registry.get_tool('test_tool') == mock_tool
        assert registry.get_tool('nonexistent') is None
    
    def test_list_tools(self):
        """Test listing available tools."""
        registry = YAMLToolRegistry()
        
        # Mock tools
        registry.tools = {
            'tool1': Mock(),
            'tool2': Mock(),
            'tool3': Mock()
        }
        
        tools = registry.list_tools()
        
        assert len(tools) == 3
        assert 'tool1' in tools
        assert 'tool2' in tools
        assert 'tool3' in tools
    
    def test_get_tool_config(self):
        """Test getting tool configuration."""
        registry = YAMLToolRegistry()
        
        # Mock tool with config
        mock_config = {'description': 'Test tool'}
        mock_tool = Mock()
        mock_tool.config = mock_config
        registry.tools['test_tool'] = mock_tool
        
        config = registry.get_tool_config('test_tool')
        
        assert config == mock_config
        assert registry.get_tool_config('nonexistent') is None
    
    def test_reload_with_path(self):
        """Test reloading tools."""
        with patch('builtins.open', mock_open(read_data='tools:\n  test: {}')):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('yaml.safe_load', return_value={'tools': {'test': {}}}):
                    registry = YAMLToolRegistry('test.yaml')
                    
                    with patch.object(registry, 'load_tools') as mock_load:
                        registry.reload()
                        mock_load.assert_called_once()
    
    def test_reload_without_path(self):
        """Test reloading without YAML path."""
        registry = YAMLToolRegistry()
        
        # Should not raise error, just log warning
        registry.reload()


class TestRegistryIntegration:
    """Integration tests for the registry package."""
    
    def test_schema_detection_integration(self):
        """Test full integration of schema detection."""
        def test_func(name: str, age: int = 25, active: bool = True) -> Dict[str, Any]:
            """A comprehensive test function."""
            return {'name': name, 'age': age, 'active': active}
        
        # Detect schema
        schema = SchemaDetector.detect_schema(test_func)
        
        # Create tool config
        config = {
            'module': 'builtins',
            'function': 'str',
            'auto_schema': True
        }
        
        # Mock the import
        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_module.str = test_func
            mock_import.return_value = mock_module
            
            # Create registry and tool
            registry = YAMLToolRegistry()
            tool = registry._create_tool_from_config('test_tool', config)
            
            # Verify tool properties
            assert tool.name == 'test_tool'
            assert 'input_schema' in tool.config
            assert 'output_schema' in tool.config
            
            # Verify schema content
            input_schema = tool.config['input_schema']
            assert input_schema['type'] == 'object'
            assert 'name' in input_schema['properties']
            assert 'age' in input_schema['properties']
            assert 'active' in input_schema['properties']
            
            # Check required parameters
            assert 'name' in input_schema['required']
            assert 'age' not in input_schema['required']  # Has default
            assert 'active' not in input_schema['required']  # Has default 