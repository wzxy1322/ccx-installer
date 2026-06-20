"""
Scan for installed UXP plugins by cross-referencing the External folder
with PS.json registration entries.
"""

import json
import os
from dataclasses import dataclass

from ..constants import UXP_EXTERNAL_PATH, PS_JSON_PATH
from .psjson import read_psjson


@dataclass
class InstalledPlugin:
    """Represents an installed UXP plugin found on disk."""

    plugin_id: str
    name: str
    version: str
    folder_name: str  # e.g. "3e6d64e0_1.9.3"
    install_path: str  # full path to plugin folder
    status: str  # "enabled", "disabled", "unregistered", "missing_folder"


def scan_installed_plugins() -> list[InstalledPlugin]:
    """Scan for installed UXP plugins.

    Cross-references folders in the External directory with PS.json entries.
    Handles three edge cases:
      - Folder exists + PS.json entry → normal (status from PS.json)
      - Folder exists + no PS.json entry → status="unregistered"
      - PS.json entry + no folder → status="missing_folder"

    Returns:
        A list of InstalledPlugin objects, sorted by name.
    """
    # Collect folder-based plugins
    folder_plugins: dict[str, InstalledPlugin] = {}

    if os.path.isdir(UXP_EXTERNAL_PATH):
        for folder_name in os.listdir(UXP_EXTERNAL_PATH):
            folder_path = os.path.join(UXP_EXTERNAL_PATH, folder_name)
            if not os.path.isdir(folder_path):
                continue

            # Try to read pluginId and version from folder name (format: {id}_{version})
            # Also try reading manifest.json as fallback
            plugin_id, version = _parse_folder_name(folder_name)
            if not plugin_id:
                # Fall back to manifest.json inside the folder
                plugin_id, version = _read_manifest_id_version(folder_path)
            if not plugin_id:
                continue

            folder_plugins[plugin_id] = InstalledPlugin(
                plugin_id=plugin_id,
                name=plugin_id,  # Fallback name, will be overwritten by PS.json if available
                version=version,
                folder_name=folder_name,
                install_path=folder_path,
                status="unregistered",
            )

    # Collect PS.json entries
    psjson_data = read_psjson()
    for entry in psjson_data.get("plugins", []):
        pid = entry.get("pluginId", "")
        if not pid:
            continue

        if pid in folder_plugins:
            # Folder exists — merge PS.json data
            fwp = folder_plugins[pid]
            fwp.name = entry.get("name", fwp.name)
            fwp.status = entry.get("status", "enabled")
            if entry.get("versionString"):
                fwp.version = entry["versionString"]
        else:
            # PS.json entry with no folder
            folder_name = f"{pid}_{entry.get('versionString', '0.0.0')}"
            folder_plugins[pid] = InstalledPlugin(
                plugin_id=pid,
                name=entry.get("name", pid),
                version=entry.get("versionString", "0.0.0"),
                folder_name=folder_name,
                install_path="",
                status="missing_folder",
            )

    # Sort by name, case-insensitive
    result = sorted(folder_plugins.values(), key=lambda p: p.name.lower())
    return result


def _parse_folder_name(folder_name: str) -> tuple[str, str]:
    """Parse pluginId and version from a folder name like 'abc123_v1.2.3'.

    Returns (plugin_id, version) or ("", "") if unparseable.
    """
    # The pattern is {pluginId}_{version}
    # Plugin IDs are typically hex strings without underscores,
    # so find the last underscore and split there
    if "_" not in folder_name:
        return ("", "")

    # Handle the case where version itself might contain underscores (unlikely)
    # Split on first underscore after the hex ID part
    parts = folder_name.rsplit("_", 1)
    if len(parts) == 2:
        plugin_id, version = parts
        if plugin_id and version:
            return (plugin_id, version)

    return ("", "")


def _read_manifest_id_version(folder_path: str) -> tuple[str, str]:
    """Try to read pluginId and version from manifest.json in the folder.

    Returns (plugin_id, version) or ("", "") on failure.
    """
    manifest_path = os.path.join(folder_path, "manifest.json")
    if not os.path.isfile(manifest_path):
        return ("", "")

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        return (manifest.get("id", ""), manifest.get("version", ""))
    except (json.JSONDecodeError, OSError):
        return ("", "")
