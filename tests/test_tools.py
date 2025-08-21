"""Test cases for the tools module."""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from xtalmcp.tools.hello_tool import HelloTool


class TestHelloTool:
    """Test cases for HelloTool class."""
    
    def test_hello_tool_initialization(self):
        """Test HelloTool initialization."""
        tool = HelloTool()
        
        assert tool.name == "hello_tool"
        assert tool.description == "A simple hello world tool that returns a greeting"
        assert hasattr(tool, 'input_schema')
        assert hasattr(tool, 'validate_input')
    
    def test_hello_tool_input_schema(self):
        """Test HelloTool input schema."""
        tool = HelloTool()
        schema = tool.input_schema
        
        assert schema['type'] == 'object'
        assert 'properties' in schema
        
        properties = schema['properties']
        assert 'name' in properties
        assert 'language' in properties
        
        # Check name property
        name_prop = properties['name']
        assert name_prop['type'] == 'string'
        assert 'Name to greet' in name_prop['description']
        
        # Check language property
        lang_prop = properties['language']
        assert lang_prop['type'] == 'string'
        assert 'Language for greeting' in lang_prop['description']
    
    def test_hello_tool_validate_input(self):
        """Test HelloTool input validation."""
        tool = HelloTool()
        
        # All inputs should be valid (all parameters are optional)
        assert tool.validate_input() is True
        assert tool.validate_input(name="Alice") is True
        assert tool.validate_input(language="fr") is True
        assert tool.validate_input(name="Bob", language="de") is True
        assert tool.validate_input(invalid_param="value") is True
    
    @pytest.mark.asyncio
    async def test_hello_tool_execute_default(self):
        """Test HelloTool execution with default parameters."""
        tool = HelloTool()
        result = await tool.execute()
        
        assert result['greeting'] == "Hello, World!"
        assert result['name'] == "World"
        assert result['language'] == "en"
        assert result['tool_name'] == "hello_tool"
        assert result['status'] == "success"
    
    @pytest.mark.asyncio
    async def test_hello_tool_execute_with_name(self):
        """Test HelloTool execution with custom name."""
        tool = HelloTool()
        result = await tool.execute(name="Alice")
        
        assert result['greeting'] == "Hello, Alice!"
        assert result['name'] == "Alice"
        assert result['language'] == "en"
        assert result['tool_name'] == "hello_tool"
        assert result['status'] == "success"
    
    @pytest.mark.asyncio
    async def test_hello_tool_execute_with_language(self):
        """Test HelloTool execution with custom language."""
        tool = HelloTool()
        result = await tool.execute(language="fr")
        
        assert result['greeting'] == "Bonjour, World!"
        assert result['name'] == "World"
        assert result['language'] == "fr"
        assert result['tool_name'] == "hello_tool"
        assert result['status'] == "success"
    
    @pytest.mark.asyncio
    async def test_hello_tool_execute_with_both_params(self):
        """Test HelloTool execution with both parameters."""
        tool = HelloTool()
        result = await tool.execute(name="Bob", language="fr")
        
        assert result['greeting'] == "Bonjour, Bob!"
        assert result['name'] == "Bob"
        assert result['language'] == "fr"
        assert result['tool_name'] == "hello_tool"
        assert result['status'] == "success"
    
    @pytest.mark.asyncio
    async def test_hello_tool_execute_unsupported_language(self):
        """Test HelloTool execution with unsupported language."""
        tool = HelloTool()
        result = await tool.execute(name="Alice", language="unsupported")
        
        # Should fall back to English
        assert result['greeting'] == "Hello, Alice!"
        assert result['name'] == "Alice"
        assert result['language'] == "unsupported"
        assert result['tool_name'] == "hello_tool"
        assert result['status'] == "success"
    
    @pytest.mark.asyncio
    async def test_hello_tool_execute_all_languages(self):
        """Test HelloTool execution with all supported languages."""
        tool = HelloTool()
        
        test_cases = [
            ("en", "Hello"),
            ("es", "¡Hola"),
            ("fr", "Bonjour"),
            ("de", "Hallo"),
            ("ja", "こんにちは")
        ]
        
        for lang, expected_greeting in test_cases:
            result = await tool.execute(name="Test", language=lang)
            assert expected_greeting in result['greeting']
            assert result['language'] == lang
            assert result['status'] == "success"
    
    @pytest.mark.asyncio
    async def test_hello_tool_run_method(self):
        """Test HelloTool run method (inherited from BaseTool)."""
        tool = HelloTool()
        result = await tool.run()
        
        assert result['greeting'] == "Hello, World!"
        assert result['status'] == "success"
    
    @pytest.mark.asyncio
    async def test_hello_tool_run_method_with_params(self):
        """Test HelloTool run method with parameters."""
        tool = HelloTool()
        result = await tool.run(name="Alice", language="fr")
        
        assert result['greeting'] == "Bonjour, Alice!"
        assert result['status'] == "success"
    
    def test_hello_tool_get_tool_schema(self):
        """Test HelloTool schema generation."""
        tool = HelloTool()
        schema = tool.get_tool_schema()
        
        assert schema['name'] == "hello_tool"
        assert schema['description'] == "A simple hello world tool that returns a greeting"


class TestHelloToolEdgeCases:
    """Test edge cases for HelloTool."""
    
    @pytest.mark.asyncio
    async def test_hello_tool_empty_name(self):
        """Test HelloTool with empty name."""
        tool = HelloTool()
        result = await tool.execute(name="")
        
        assert result['greeting'] == "Hello, !"
        assert result['name'] == ""
        assert result['status'] == "success"
    
    @pytest.mark.asyncio
    async def test_hello_tool_none_name(self):
        """Test HelloTool with None name."""
        tool = HelloTool()
        result = await tool.execute(name=None)
        
        assert result['greeting'] == "Hello, None!"
        assert result['name'] is None
        assert result['status'] == "success"
    
    @pytest.mark.asyncio
    async def test_hello_tool_special_characters(self):
        """Test HelloTool with special characters in name."""
        tool = HelloTool()
        special_names = ["O'Connor", "José", "Müller", "李", "🎉"]
        
        for name in special_names:
            result = await tool.execute(name=name)
            assert result['greeting'] == f"Hello, {name}!"
            assert result['name'] == name
            assert result['status'] == "success"
    
    @pytest.mark.asyncio
    async def test_hello_tool_very_long_name(self):
        """Test HelloTool with very long name."""
        tool = HelloTool()
        long_name = "A" * 1000
        
        result = await tool.execute(name=long_name)
        assert result['greeting'] == f"Hello, {long_name}!"
        assert result['name'] == long_name
        assert result['status'] == "success"


class TestHelloToolIntegration:
    """Integration tests for HelloTool."""
    
    @pytest.mark.asyncio
    async def test_hello_tool_lifecycle(self):
        """Test complete HelloTool lifecycle."""
        # Create tool
        tool = HelloTool()
        
        # Verify properties
        assert tool.name == "hello_tool"
        assert tool.description is not None
        assert hasattr(tool, 'input_schema')
        assert hasattr(tool, 'validate_input')
        
        # Test validation
        assert tool.validate_input() is True
        
        # Test execution
        result = await tool.execute(name="Integration", language="es")
        assert result['greeting'] == "¡Hola, Integration!"
        assert result['status'] == "success"
        
        # Test schema generation
        schema = tool.get_tool_schema()
        assert schema['name'] == tool.name
        assert schema['description'] == tool.description
    
    @pytest.mark.asyncio
    async def test_hello_tool_parameter_combinations(self):
        """Test various parameter combinations."""
        tool = HelloTool()
        
        # Test all combinations of optional parameters
        combinations = [
            {},
            {"name": "Alice"},
            {"language": "fr"},
            {"name": "Bob", "language": "de"}
        ]
        
        for params in combinations:
            result = await tool.execute(**params)
            assert result['status'] == "success"
            assert result['tool_name'] == "hello_tool"
            
            # Verify expected parameters
            expected_name = params.get("name", "World")
            assert result['name'] == expected_name
            
            # Verify greeting contains the name
            assert expected_name in result['greeting']
    
    @pytest.mark.asyncio
    async def test_hello_tool_error_handling(self):
        """Test HelloTool error handling."""
        tool = HelloTool()
        
        # Tool should handle any input gracefully
        # (since all parameters are optional and validation always returns True)
        
        # Test with invalid parameter types
        result = await tool.execute(name=123, language=456)
        assert result['status'] == "success"
        
        # Test with complex objects
        result = await tool.execute(name={"complex": "object"}, language=["list"])
        assert result['status'] == "success"
        
        # Test with function objects
        def test_func():
            pass
        
        result = await tool.execute(name=test_func, language=test_func)
        assert result['status'] == "success" 