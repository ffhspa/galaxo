"""Top-level package for the Galaxo application.

This module exposes existing modules under the ``GALAXO`` namespace for
compatibility with imports like ``from GALAXO.CONFIG.Constants import Constants``.
"""

import os
import sys

# Add the project root (one level up) so imports work regardless of symlinks
PACKAGE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(PACKAGE_DIR, ".."))

# Extend the package search path to include the project root. This allows
# ``import GALAXO.PROCESS`` even on platforms where symlinks are unavailable
# (e.g. Windows).
if ROOT_DIR not in __path__:
    __path__.append(ROOT_DIR)

# Also prepend the root to ``sys.path`` so top-level scripts can import modules
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

