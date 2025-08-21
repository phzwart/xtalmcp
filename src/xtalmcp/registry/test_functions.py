"""
Test functions for demonstrating auto-schema detection.

These functions show how the YAML registry can automatically
detect parameter types and create proper schemas.
"""

from typing import Dict, List, Optional, Union
import numpy as np


def extract_cc12_table(log_file: str, 
                       output_format: str = "json",
                       min_resolution: Optional[float] = None) -> Dict[str, Union[str, float, List[float]]]:
    """
    Extract CC(1/2) correlation table from AIMLESS log file.
    
    This function demonstrates automatic schema detection with:
    - Required parameters (log_file)
    - Optional parameters with defaults (output_format)
    - Optional parameters without defaults (min_resolution)
    - Complex return types
    """
    # Mock implementation
    return {
        "status": "success",
        "cc12_values": [0.95, 0.92, 0.88, 0.85],
        "resolution_bins": [2.0, 2.5, 3.0, 3.5],
        "output_format": output_format
    }


def plot_cc12_vs_resolution(log_file: str,
                           output_format: str = "png",
                           resolution_range: Optional[Dict[str, float]] = None) -> Dict[str, str]:
    """
    Generate CC(1/2) vs resolution plot.
    
    Demonstrates:
    - Nested parameter types (Dict)
    - Enum-like string parameters
    - Complex input validation
    """
    # Mock implementation
    return {
        "plot_data": "base64_encoded_plot_data_here",
        "status": "success",
        "format": output_format
    }


def extract_unit_cell_parameters(cif_file: str,
                                space_group: Optional[str] = None,
                                tolerance: float = 0.01) -> Dict[str, Union[str, float, List[float]]]:
    """
    Extract unit cell parameters from CIF file.
    
    Shows:
    - File input parameters
    - Numeric parameters with defaults
    - Optional string parameters
    """
    # Mock implementation
    return {
        "a": 10.0,
        "b": 12.0,
        "c": 15.0,
        "alpha": 90.0,
        "beta": 90.0,
        "gamma": 90.0,
        "space_group": space_group or "P1",
        "tolerance": tolerance
    }


def validate_structure(structure_file: str,
                      validation_level: str = "standard",
                      output_format: str = "json") -> Dict[str, Union[str, List[str], bool]]:
    """
    Validate crystallographic structure.
    
    Demonstrates:
    - Enum-like string parameters
    - Multiple output types
    - Complex validation logic
    """
    # Mock implementation
    return {
        "valid": True,
        "warnings": ["Minor deviation in bond lengths"],
        "errors": [],
        "validation_level": validation_level,
        "output_format": output_format
    } 