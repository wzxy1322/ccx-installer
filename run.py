#!/usr/bin/env python3
"""
Thin wrapper to launch the CCX Plugin Installer.

This script is the PyInstaller entry point.  It ensures the src package
is importable and then delegates to src.main.main().
"""

import os
import sys

# Add the project root to sys.path so 'src' can be imported
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.main import main

if __name__ == "__main__":
    main()
