"""
Schema detection utilities for XtalMCP tools.

This module provides automatic schema detection from Python function
signatures, type hints, and docstrings.
"""

import inspect
from typing import Any, Dict, get_type_hints, Union, Optional


class SchemaDetector:
    """Automatically detect input/output schemas from Python functions."""
    
    @staticmethod
    def detect_schema(func: callable, module_name: str = "") -> Dict[str, Any]:
        """
        Detect schema from function signature and docstring.
        
        Args:
            func: Python function to analyze
            module_name: Name of the module for context
            
        Returns:
            Dictionary containing detected schema information
        """
        # Get type hints
        type_hints = get_type_hints(func)
        
        # Extract first line of docstring as description
        doc = func.__doc__ or ""
        first_line = doc.strip().split('\n')[0] if doc else ""
        
        # Build input schema from type hints
        input_properties = {}
        required_params = []
        
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
                
            param_type = type_hints.get(param_name, Any)
            param_info = {
                'type': SchemaDetector._map_python_type_to_json(param_type),
                'description': f"Parameter {param_name}"
            }
            
            # Handle default values
            if param.default != inspect.Parameter.empty:
                param_info['default'] = param.default
            else:
                required_params.append(param_name)
            
            # Handle optional types
            if SchemaDetector._is_optional_type(param_type):
                base_type = SchemaDetector._get_optional_base_type(param_type)
                param_info['type'] = SchemaDetector._map_python_type_to_json(base_type)
            
            input_properties[param_name] = param_info
        
        # Build output schema
        return_type = type_hints.get('return', Any)
        output_schema = {
            'type': SchemaDetector._map_python_type_to_json(return_type),
            'description': f"Output from {func.__name__}"
        }
        
        return {
            'description': first_line,
            'input_schema': {
                'type': 'object',
                'properties': input_properties,
                'required': required_params
            },
            'output_schema': output_schema
        }
    
    @staticmethod
    def _map_python_type_to_json(python_type: type) -> str:
        """Map Python types to JSON schema types."""
        type_mapping = {
            str: 'string',
            int: 'integer',
            float: 'number',
            bool: 'boolean',
            list: 'array',
            dict: 'object',
            tuple: 'array',
            Any: 'string',  # Default to string for unknown types
        }
        
        # Handle Union types (including Optional)
        if hasattr(python_type, '__origin__') and python_type.__origin__ is Union:
            # For Optional[T], extract the base type
            base_type = SchemaDetector._get_optional_base_type(python_type)
            return SchemaDetector._map_python_type_to_json(base_type)
        
        # Handle generic types like List[str]
        if hasattr(python_type, '__origin__'):
            origin_type = python_type.__origin__
            return type_mapping.get(origin_type, 'string')
        
        # Handle actual type instances
        if python_type in type_mapping:
            return type_mapping[python_type]
        
        # Fallback for unknown types
        return 'string'
    
    @staticmethod
    def _is_optional_type(python_type: type) -> bool:
        """Check if a type is Optional (Union with None)."""
        if hasattr(python_type, '__origin__') and python_type.__origin__ is Union:
            return type(None) in python_type.__args__
        return False
    
    @staticmethod
    def _get_optional_base_type(python_type: type) -> type:
        """Extract the base type from Optional[T]."""
        if hasattr(python_type, '__origin__') and python_type.__origin__ is Union:
            # Filter out None from Union types
            base_types = [t for t in python_type.__args__ if t is not type(None)]
            return base_types[0] if base_types else str
        return python_type 