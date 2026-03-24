entropic
========

Entropic is a minimal, file-based run cache for Python-driven simulations and scripts.
By hashing your input parameters, it automatically identifies duplicate runs and skips
unnecessary computation. It is completely agnostic to your simulation engine,
lightweight by design, and built to manage locally run research workflows without
getting in your way.

Installation::

   pip install entropic
   uv add entropic

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   api
