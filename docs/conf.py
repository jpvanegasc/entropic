# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
import os
import sys
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _get_version

sys.path.insert(0, os.path.abspath("../src"))

project = "entropic"
copyright = "2024, Juan Pablo Vanegas"
author = "Juan Pablo Vanegas"

try:
    release = _get_version("entropic")
except PackageNotFoundError:
    print("To build the documentation, the distribution information of entropic")
    print("has to be available. Either install the package into your")
    print('development environment or run "pip install -e ." to setup the')
    print("metadata. A virtualenv is recommended!")
    import sys

    sys.exit(1)

# -- General configuration ---------------------------------------------------

extensions = ["myst_parser"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

html_theme = "alabaster"
html_static_path = ["_static"]
