# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import pkg_resources

sys.path.insert(0, os.path.abspath(".."))

project = "entropic"
copyright = "2023, Juan Pablo Vanegas"
author = "Juan Pablo Vanegas"

try:
    release = pkg_resources.get_distribution("entropic").version
except pkg_resources.DistributionNotFound:
    print("To build the documentation, The distribution information of entropic")
    print("has to be available. Either install the package into your")
    print('development environment or run "pip install -e ." to setup the')
    print("metadata. A virtualenv is recommended!")
    sys.exit(1)
del pkg_resources

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
]
myst_enable_extensions = [
    "amsmath",
    "dollarmath",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
