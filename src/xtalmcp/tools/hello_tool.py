"""
Hello World tool for XtalMCP.

This module provides a simple hello world tool that demonstrates
the basic tool interface.
"""

from typing import Dict, Any
from ..base import BaseTool


class HelloTool(BaseTool):
    """
    Simple hello world tool.
    
    This tool demonstrates the basic tool interface by returning
    a greeting message.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "hello_tool"
        self.description = "A simple hello world tool that returns a greeting"
        self.input_schema = {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name to greet (optional)"
                },
                "language": {
                    "type": "string",
                    "description": "Language for greeting (optional, default: 'en')"
                }
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the hello tool.
        
        Args:
            **kwargs: Tool parameters including optional 'name' and 'language'
            
        Returns:
            Dict containing the greeting message
        """
        name = kwargs.get("name", "World")
        language = kwargs.get("language", "en")
        
        greetings = {
            "en": f"Hello, {name}!",
            "es": f"¡Hola, {name}!",
            "fr": f"Bonjour, {name}!",
            "de": f"Hallo, {name}!",
            "ja": f"こんにちは、{name}さん！"
        }
        
        # Handle unhashable types gracefully
        try:
            greeting = greetings.get(language, greetings["en"])
        except (TypeError, KeyError):
            # Fall back to English if language is unhashable or not found
            greeting = greetings["en"]
        
        return {
            "greeting": greeting,
            "name": name,
            "language": language,
            "tool_name": self.name,
            "status": "success"
        }
    
    def validate_input(self, **kwargs) -> bool:
        """
        Validate input parameters.
        
        Args:
            **kwargs: Input parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        # All parameters are optional, so always valid
        return True