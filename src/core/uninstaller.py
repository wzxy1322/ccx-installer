"""
Uninstall orchestration for UXP plugins.

Handles:
  1. Removing the plugin folder from External/
  2. Removing the entry from PS.json
"""

import os
import shutil
from typing import Callable

from ..constants import UXP_EXTERNAL_PATH
from .psjson import read_psjson, remove_plugin_entry, write_psjson_with_retry, PluginNotFoundError


class UninstallError(Exception):
    """Raised when uninstallation fails."""

    def __init__(self, message: str, recovery_hint: str | None = None):
        super().__init__(message)
        self.recovery_hint = recovery_hint


def uninstall_plugin(
    plugin_id: str,
    plugin_version: str | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> str:
    """Uninstall a UXP plugin.

    Args:
        plugin_id: The plugin ID to remove.
        plugin_version: Optional specific version. If None, finds and removes
                        any folder starting with {plugin_id}_.
        progress_callback: Optional callback receiving status messages.

    Returns:
        The name of the removed plugin.

    Raises:
        UninstallError: On any failure.
    """
    def _report(msg: str) -> None:
        if progress_callback:
            progress_callback(msg)

    try:
        # Step 1: Remove folder from External/
        _report("Removing plugin files...")
        plugin_name = _remove_plugin_folder(plugin_id, plugin_version)

        # Step 2: Remove from PS.json
        _report("Updating PS.json...")
        try:
            psjson_data = read_psjson()
            psjson_data = remove_plugin_entry(psjson_data, plugin_id)
            write_psjson_with_retry(psjson_data)
        except PluginNotFoundError:
            # Folder is gone; the PS.json entry may have already been removed
            _report("No PS.json entry found for this plugin; skipping.")

        _report("Uninstall complete.")
        return plugin_name

    except PermissionError as e:
        raise UninstallError(
            f"Permission denied while removing plugin:\n{e}",
            "Please close Adobe Photoshop and try again.",
        ) from e


def _remove_plugin_folder(plugin_id: str, plugin_version: str | None = None) -> str:
    """Remove the plugin folder from External/.

    Returns the name of the removed folder.
    """
    if not os.path.isdir(UXP_EXTERNAL_PATH):
        raise UninstallError(
            "No UXP plugins directory found. Nothing to uninstall."
        )

    # Find matching folder(s)
    prefix = f"{plugin_id}_"
    matching: list[str] = []
    for folder_name in os.listdir(UXP_EXTERNAL_PATH):
        if folder_name.startswith(prefix) or folder_name == plugin_id:
            folder_path = os.path.join(UXP_EXTERNAL_PATH, folder_name)
            if os.path.isdir(folder_path):
                matching.append(folder_name)

    if not matching:
        raise UninstallError(
            f"No plugin folder found for '{plugin_id}' in the External directory."
        )

    # If a version is specified, prefer exact match
    target = matching[0]
    if plugin_version:
        exact = f"{plugin_id}_{plugin_version}"
        if exact in matching:
            target = exact

    folder_path = os.path.join(UXP_EXTERNAL_PATH, target)
    shutil.rmtree(folder_path, ignore_errors=False)
    return target
