"""
Temporary directory context manager.
"""

import os
import shutil
import tempfile
from contextlib import contextmanager
from typing import Generator


@contextmanager
def temp_work_dir() -> Generator[str, None, None]:
    """Create a temporary directory, yield its path, and clean up on exit.

    Usage:
        with temp_work_dir() as tmp:
            # extract files, parse, etc.
            pass
    """
    path = tempfile.mkdtemp(prefix="ccx_installer_")
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
