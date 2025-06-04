"""Top-level package for the Galaxo application.

This module exposes existing modules under the ``GALAXO`` namespace for
compatibility with imports like ``from GALAXO.CONFIG.Constants import Constants``.
"""

import os
import sys

# Ensure the project root (one level up) is on the import path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

