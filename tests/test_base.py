"""Test cases for the base classes."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from typing import Dict, Any

from xtalmcp.base import BaseTool, FileInputTool


class TestBaseTool:
    """Test cases for BaseTool class."""
    
    def test_base_tool_initialization(self):
        """Test BaseTool initialization."""
        class TestTool(BaseTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestTool()
        
        assert tool.name == "testtool"
        assert tool.description == "A simple tool"
    
    def test_base_tool_name_override(self):
        """Test BaseTool with custom name."""
        class TestTool(BaseTool):
            def __init__(self):
                super().__init__()
                self.name = "custom_name"
            
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestTool()
        
        assert tool.name == "custom_name"
    
    def test_base_tool_description_override(self):
        """Test BaseTool with custom description."""
        class TestTool(BaseTool):
            def __init__(self):
                super().__init__()
                self.description = "Custom description"
            
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestTool()
        
        assert tool.description == "Custom description"
    
    def test_base_tool_schema(self):
        """Test BaseTool schema generation."""
        class TestTool(BaseTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestTool()
        schema = tool.get_tool_schema()
        
        assert schema['name'] == "testtool"
        assert schema['description'] == "A simple tool"
    
    @pytest.mark.asyncio
    async def test_base_tool_run_success(self):
        """Test BaseTool run method with successful execution."""
        class TestTool(BaseTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "success"}
        
        tool = TestTool()
        result = await tool.run(param="test")
        
        assert result['result'] == "success"
    
    @pytest.mark.asyncio
    async def test_base_tool_run_error(self):
        """Test BaseTool run method with error handling."""
        class TestTool(BaseTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                raise ValueError("Test error")
        
        tool = TestTool()
        result = await tool.run(param="test")
        
        assert result['status'] == 'error'
        assert 'Test error' in result['error']
        assert result['tool'] == 'testtool'
    
    def test_base_tool_abstract_method(self):
        """Test that BaseTool cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseTool()


class TestFileInputTool:
    """Test cases for FileInputTool class."""
    
    def test_file_input_tool_initialization(self):
        """Test FileInputTool initialization."""
        class TestFileTool(FileInputTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestFileTool()
        
        assert tool.name == "testfiletool"
        assert tool.description == "A file processing tool"
    
    @pytest.mark.asyncio
    async def test_file_input_tool_get_file_content_from_content(self):
        """Test getting file content from direct content."""
        class TestFileTool(FileInputTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestFileTool()
        
        content = "test file content"
        result = await tool.get_file_content(content=content)
        
        assert result == content
    
    @pytest.mark.asyncio
    async def test_file_input_tool_get_file_content_from_file_path(self):
        """Test getting file content from file path."""
        class TestFileTool(FileInputTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestFileTool()
        
        test_content = "test file content"
        
        with patch('builtins.open', mock_open(read_data=test_content)):
            result = await tool.get_file_content(file_path="test.txt")
            
            assert result == test_content
    
    @pytest.mark.asyncio
    async def test_file_input_tool_get_file_content_no_input(self):
        """Test getting file content with no input."""
        class TestFileTool(FileInputTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestFileTool()
        
        with pytest.raises(ValueError, match="Either file_path or content must be provided"):
            await tool.get_file_content()
    
    @pytest.mark.asyncio
    async def test_file_input_tool_get_file_content_file_not_found(self):
        """Test getting file content from non-existent file."""
        class TestFileTool(FileInputTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestFileTool()
        
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(ValueError, match="Could not read file"):
                await tool.get_file_content(file_path="nonexistent.txt")
    
    @pytest.mark.asyncio
    async def test_file_input_tool_get_file_content_encoding_error(self):
        """Test getting file content with encoding error."""
        class TestFileTool(FileInputTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestFileTool()
        
        with patch('builtins.open', side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "test")):
            with pytest.raises(ValueError, match="Could not read file"):
                await tool.get_file_content(file_path="test.txt")
    
    def test_file_input_tool_inheritance(self):
        """Test that FileInputTool inherits from BaseTool."""
        class TestFileTool(FileInputTool):
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {"result": "test"}
        
        tool = TestFileTool()
        
        assert isinstance(tool, BaseTool)
        assert hasattr(tool, 'get_file_content')


class TestBaseToolIntegration:
    """Integration tests for base classes."""
    
    @pytest.mark.asyncio
    async def test_tool_lifecycle(self):
        """Test complete tool lifecycle."""
        class TestTool(BaseTool):
            def __init__(self):
                super().__init__()
                self.name = "lifecycle_tool"
                self.description = "Test tool lifecycle"
            
            async def execute(self, **kwargs) -> Dict[str, Any]:
                return {
                    "input": kwargs,
                    "processed": True
                }
        
        # Create tool
        tool = TestTool()
        
        # Test schema
        schema = tool.get_tool_schema()
        assert schema['name'] == "lifecycle_tool"
        assert schema['description'] == "Test tool lifecycle"
        
        # Test execution
        result = await tool.run(param1="value1", param2="value2")
        assert result['processed'] is True
        assert result['input']['param1'] == "value1"
        assert result['input']['param2'] == "value2"
    
    @pytest.mark.asyncio
    async def test_file_tool_integration(self):
        """Test file tool integration."""
        class TestFileTool(FileInputTool):
            def __init__(self):
                super().__init__()
                self.name = "file_integration_tool"
                self.description = "Test file tool integration"
            
            async def execute(self, **kwargs) -> Dict[str, Any]:
                # Get file content
                file_content = await self.get_file_content(**kwargs)
                return {
                    "content": file_content,
                    "length": len(file_content)
                }
        
        tool = TestFileTool()
        
        # Test with direct content
        result = await tool.run(content="test content")
        assert result['content'] == "test content"
        assert result['length'] == 12
        
        # Test with file path
        test_content = "file content"
        with patch('builtins.open', mock_open(read_data=test_content)):
            result = await tool.run(file_path="test.txt")
            assert result['content'] == test_content
            assert result['length'] == len(test_content)
    
    @pytest.mark.asyncio
    async def test_error_handling_integration(self):
        """Test error handling integration."""
        class ErrorTool(BaseTool):
            def __init__(self):
                super().__init__()
                self.name = "error_tool"
                self.description = "Tool that raises errors"
            
            async def execute(self, **kwargs) -> Dict[str, Any]:
                if 'raise_error' in kwargs:
                    raise RuntimeError("Intentional error")
                return {"status": "ok"}
        
        tool = ErrorTool()
        
        # Test normal execution
        result = await tool.run(normal_param="value")
        assert result['status'] == 'ok'
        
        # Test error execution
        result = await tool.run(raise_error=True)
        assert result['status'] == 'error'
        assert 'Intentional error' in result['error']
        assert result['tool'] == 'error_tool' 