"""Sphinx configuration."""
project = "xtalmcp"
author = "Petrus H Zwart"
copyright = "2025, Petrus H Zwart"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
