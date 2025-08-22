"""
Runtime Schema Validator for XtalMCP Tools.

This module validates YAML tool configurations against actual function signatures
to catch schema mismatches before they cause runtime errors.
"""

import inspect
import logging
from typing import Any, Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a schema validation error."""
    tool_name: str
    field: str
    message: str
    severity: str = "ERROR"


@dataclass
class ValidationResult:
    """Result of schema validation."""
    tool_name: str
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]


class SchemaValidator:
    """Validates YAML tool configurations against function signatures."""
    
    def __init__(self):
        self.validation_results: List[ValidationResult] = []
    
    def validate_tool_config(self, tool_name: str, config: Dict[str, Any], function: callable) -> ValidationResult:
        """
        Validate a single tool configuration against its function signature.
        
        Args:
            tool_name: Name of the tool
            config: Tool configuration from YAML
            function: Actual Python function to validate against
            
        Returns:
            ValidationResult with validation status and errors
        """
        errors = []
        warnings = []
        
        try:
            # Get function signature
            sig = inspect.signature(function)
            params = sig.parameters
            
            # Validate input schema
            input_schema = config.get('input_schema', {})
            if input_schema:
                input_errors, input_warnings = self._validate_input_schema(
                    tool_name, input_schema, params, config
                )
                errors.extend(input_errors)
                warnings.extend(input_warnings)
            
            # Validate output schema
            output_schema = config.get('output_schema', {})
            if output_schema:
                output_errors, output_warnings = self._validate_output_schema(
                    tool_name, output_schema, function
                )
                errors.extend(output_errors)
                warnings.extend(output_warnings)
            
            # Check for missing required fields
            required_fields = ['module', 'function']
            for field in required_fields:
                if field not in config:
                    errors.append(ValidationError(
                        tool_name=tool_name,
                        field=field,
                        message=f"Missing required field: {field}",
                        severity="ERROR"
                    ))
            
            # Validate function can be imported
            try:
                module_name = config.get('module')
                function_name = config.get('function')
                if module_name and function_name:
                    import importlib
                    module = importlib.import_module(module_name)
                    if not hasattr(module, function_name):
                        errors.append(ValidationError(
                            tool_name=tool_name,
                            field='function',
                            message=f"Function {function_name} not found in module {module_name}",
                            severity="ERROR"
                        ))
            except ImportError as e:
                errors.append(ValidationError(
                    tool_name=tool_name,
                    field='module',
                    message=f"Cannot import module {module_name}: {e}",
                    severity="ERROR"
                ))
            
        except Exception as e:
            errors.append(ValidationError(
                tool_name=tool_name,
                field='validation',
                message=f"Validation failed with exception: {e}",
                severity="ERROR"
            ))
        
        is_valid = len([e for e in errors if e.severity == "ERROR"]) == 0
        
        result = ValidationResult(
            tool_name=tool_name,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
        
        self.validation_results.append(result)
        return result
    
    def _validate_input_schema(self, tool_name: str, input_schema: Dict[str, Any], 
                              params: Dict[str, inspect.Parameter], config: Dict[str, Any]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate input schema against function parameters."""
        errors = []
        warnings = []
        
        if input_schema.get('type') != 'object':
            errors.append(ValidationError(
                tool_name=tool_name,
                field='input_schema',
                message="Input schema must be of type 'object'",
                severity="ERROR"
            ))
            return errors, warnings
        
        properties = input_schema.get('properties', {})
        required = input_schema.get('required', [])
        
        # Check if required parameters exist in function signature
        for param_name in required:
            if param_name not in params:
                errors.append(ValidationError(
                    tool_name=tool_name,
                    field=f'required.{param_name}',
                    message=f"Required parameter '{param_name}' not found in function signature",
                    severity="ERROR"
                ))
        
        # Check if schema properties match function parameters
        for prop_name, prop_schema in properties.items():
            if prop_name not in params:
                warnings.append(ValidationError(
                    tool_name=tool_name,
                    field=f'properties.{prop_name}',
                    message=f"Schema property '{prop_name}' not found in function signature",
                    severity="WARNING"
                ))
            
            # Validate parameter types if possible
            param = params.get(prop_name)
            if param and param.annotation != inspect.Parameter.empty:
                expected_type = param.annotation
                schema_type = prop_schema.get('type')
                
                if not self._types_compatible(schema_type, expected_type):
                    warnings.append(ValidationError(
                        tool_name=tool_name,
                        field=f'properties.{prop_name}.type',
                        message=f"Schema type '{schema_type}' may not match function type '{expected_type}'",
                        severity="WARNING"
                    ))
        
        return errors, warnings
    
    def _validate_output_schema(self, tool_name: str, output_schema: Dict[str, Any], 
                               function: callable) -> Tuple[List[ValidationError], List[ValidationError]]:
        """Validate output schema against function return type."""
        errors = []
        warnings = []
        
        # Check if output schema type is valid
        valid_types = ['object', 'array', 'string', 'number', 'integer', 'boolean']
        output_type = output_schema.get('type')
        
        if output_type not in valid_types:
            errors.append(ValidationError(
                tool_name=tool_name,
                field='output_schema.type',
                message=f"Invalid output schema type: {output_type}. Must be one of {valid_types}",
                severity="ERROR"
            ))
        
        # For object outputs, check if they have required properties
        if output_type == 'object':
            required = output_schema.get('required', [])
            properties = output_schema.get('properties', {})
            
            for req_prop in required:
                if req_prop not in properties:
                    errors.append(ValidationError(
                        tool_name=tool_name,
                        field=f'output_schema.required.{req_prop}',
                        message=f"Required output property '{req_prop}' not defined in properties",
                        severity="ERROR"
                    ))
        
        return errors, warnings
    
    def _types_compatible(self, schema_type: str, python_type: type) -> bool:
        """Check if schema type is compatible with Python type."""
        if schema_type == 'number':
            return python_type in (int, float, complex)
        elif schema_type == 'integer':
            return python_type == int
        elif schema_type == 'string':
            return python_type == str
        elif schema_type == 'boolean':
            return python_type == bool
        elif schema_type == 'array':
            return hasattr(python_type, '__iter__') and not isinstance(python_type, str)
        elif schema_type == 'object':
            return hasattr(python_type, '__dict__')
        return True
    
    def validate_all_tools(self, tools_config: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate all tools in a configuration.
        
        Args:
            tools_config: Full tools configuration dictionary
            
        Returns:
            List of validation results for all tools
        """
        results = []
        
        if 'tools' not in tools_config:
            logger.error("No 'tools' section found in configuration")
            return results
        
        for tool_name, tool_config in tools_config['tools'].items():
            try:
                # Import the function to validate against
                module_name = tool_config.get('module')
                function_name = tool_config.get('function')
                
                if module_name and function_name:
                    import importlib
                    module = importlib.import_module(module_name)
                    function = getattr(module, function_name)
                    
                    # Validate the tool
                    result = self.validate_tool_config(tool_name, tool_config, function)
                    results.append(result)
                    
                    # Log validation results
                    if result.is_valid:
                        logger.info(f"✅ Tool '{tool_name}' validation passed")
                    else:
                        logger.error(f"❌ Tool '{tool_name}' validation failed:")
                        for error in result.errors:
                            logger.error(f"  - {error.field}: {error.message}")
                    
                    for warning in result.warnings:
                        logger.warning(f"⚠️  Tool '{tool_name}' warning: {warning.field}: {warning.message}")
                        
                else:
                    logger.error(f"Tool '{tool_name}' missing module or function specification")
                    
            except Exception as e:
                logger.error(f"Failed to validate tool '{tool_name}': {e}")
                results.append(ValidationResult(
                    tool_name=tool_name,
                    is_valid=False,
                    errors=[ValidationError(tool_name, 'validation', str(e))],
                    warnings=[]
                ))
        
        return results
    
    def print_validation_summary(self):
        """Print a summary of all validation results."""
        total_tools = len(self.validation_results)
        valid_tools = len([r for r in self.validation_results if r.is_valid])
        error_count = sum(len(r.errors) for r in self.validation_results)
        warning_count = sum(len(r.warnings) for r in self.validation_results)
        
        print(f"\n🔍 Schema Validation Summary:")
        print(f"  Total Tools: {total_tools}")
        print(f"  ✅ Valid: {valid_tools}")
        print(f"  ❌ Errors: {error_count}")
        print(f"  ⚠️  Warnings: {warning_count}")
        
        if error_count > 0:
            print(f"\n❌ Tools with Errors:")
            for result in self.validation_results:
                if result.errors:
                    print(f"  {result.tool_name}:")
                    for error in result.errors:
                        print(f"    - {error.field}: {error.message}")
        
        if warning_count > 0:
            print(f"\n⚠️  Tools with Warnings:")
            for result in self.validation_results:
                if result.warnings:
                    print(f"  {result.tool_name}:")
                    for warning in result.warnings:
                        print(f"    - {warning.field}: {warning.message}")
        
        if valid_tools == total_tools:
            print(f"\n🎉 All tools validated successfully!")
        else:
            print(f"\n💥 Validation failed! Fix errors before starting server.")
