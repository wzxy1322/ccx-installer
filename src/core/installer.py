"""
Installation orchestration for .ccx plugins.

Handles the full install pipeline:
  1. Remove old versions of the same plugin from External/
  2. Extract the .ccx to External/{pluginId}_{version}/
  3. Register/update the entry in PS.json
"""

import os
import shutil
from typing import Callable

from ..constants import UXP_EXTERNAL_PATH
from .ccx_parser import CcxInfo, extract_ccx
from .psjson import read_psjson, add_plugin_entry, write_psjson_with_retry


class InstallError(Exception):
    """Raised when installation fails. Includes a user-friendly message."""

    def __init__(self, message: str, recovery_hint: str | None = None):
        super().__init__(message)
        self.recovery_hint = recovery_hint


def install_plugin(
    ccx_path: str,
    info: CcxInfo,
    progress_callback: Callable[[str], None] | None = None,
) -> str:
    """Run the full install pipeline for a .ccx plugin.

    Args:
        ccx_path: Path to the .ccx file to install.
        info: Parsed plugin metadata from parse_ccx().
        progress_callback: Optional callback receiving status messages.

    Returns:
        The destination directory path on success.

    Raises:
        InstallError: On any failure during the pipeline.
    """
    def _report(msg: str) -> None:
        if progress_callback:
            progress_callback(msg)

    plugin_folder_name = f"{info.plugin_id}_{info.version}"
    dest_path = os.path.join(UXP_EXTERNAL_PATH, plugin_folder_name)

    try:
        # Step 1: Remove old versions
        _report("Removing old versions...")
        _remove_old_versions(info.plugin_id)

        # Step 2: Ensure External directory exists
        _report("Preparing plugin directory...")
        os.makedirs(UXP_EXTERNAL_PATH, exist_ok=True)

        # Step 3: Extract .ccx
        _report(f"Extracting plugin files to External\\{plugin_folder_name}...")
        extract_ccx(ccx_path, dest_path)

        # Step 4: Register in PS.json
        _report("Registering in PS.json...")
        psjson_data = read_psjson()
        psjson_data = add_plugin_entry(psjson_data, info)
        write_psjson_with_retry(psjson_data)

        _report("Installation complete.")

    except PermissionError as e:
        raise InstallError(
            f"Permission denied while installing plugin:\n{e}",
            "Try running the installer as Administrator.",
        ) from e

    except OSError as e:
        # Disk full, path too long, etc.
        hint = None
        if hasattr(e, "winerror") and e.winerror == 112:
            hint = "Not enough disk space to install this plugin."
        elif hasattr(e, "winerror") and e.winerror == 206:
            hint = "The install path is too long. Try using a shorter plugin name."
        raise InstallError(f"File system error:\n{e}", hint) from e

    return dest_path


def _remove_old_versions(plugin_id: str) -> list[str]:
    """Delete any existing plugin folders in External/ starting with plugin_id_.

    Args:
        plugin_id: The plugin ID to match.

    Returns:
        List of paths that were removed.
    """
    removed: list[str] = []
    if not os.path.isdir(UXP_EXTERNAL_PATH):
        return removed

    prefix = f"{plugin_id}_"
    for folder_name in os.listdir(UXP_EXTERNAL_PATH):
        if folder_name.startswith(prefix):
            folder_path = os.path.join(UXP_EXTERNAL_PATH, folder_name)
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path, ignore_errors=True)
                removed.append(folder_path)

    return removed
