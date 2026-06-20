"""
PS.json read/write/update operations with atomic writes.

PS.json is the UXP plugin registry located at:
    %APPDATA%\\Adobe\\UXP\\PluginsInfo\\v1\\PS.json

It contains a "plugins" array of registration entries, one per installed plugin.
"""

import json
import os
import shutil
import time
from datetime import datetime
from typing import Any

from ..constants import (
    build_psjson_entry,
    PS_JSON_PATH,
    UXP_EXTERNAL_PATH,
    UXP_PLUGINS_INFO_PATH,
)
from .ccx_parser import CcxInfo


class PluginNotFoundError(Exception):
    """Raised when trying to remove a pluginId that doesn't exist in PS.json."""


def read_psjson() -> dict[str, Any]:
    """Read PS.json from disk.

    Returns:
        A dict with a "plugins" key.  Returns {"plugins": []} if the file
        is missing or empty.  If the JSON is corrupted, the damaged file
        is backed up as PS.json.bak.YYYYMMDD_HHMMSS and a fresh empty
        structure is returned.
    """
    if not os.path.isfile(PS_JSON_PATH):
        return {"plugins": []}

    try:
        with open(PS_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # Back up the corrupted file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = PS_JSON_PATH + f".bak.{timestamp}"
        shutil.copy2(PS_JSON_PATH, backup_path)
        return {"plugins": []}

    # Ensure the expected structure
    if not isinstance(data, dict) or "plugins" not in data:
        data = {"plugins": data.get("plugins", [])}
    if not isinstance(data["plugins"], list):
        data["plugins"] = []

    return data


def write_psjson(data: dict[str, Any]) -> None:
    """Write data to PS.json atomically.

    Uses a .tmp file + os.replace() to prevent corruption if the process
    is interrupted mid-write.  Creates parent directories if needed.

    Args:
        data: The full PS.json data dict to write.
    """
    os.makedirs(UXP_PLUGINS_INFO_PATH, exist_ok=True)

    tmp_path = PS_JSON_PATH + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, PS_JSON_PATH)
    except Exception:
        # Clean up tmp file on failure
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def add_plugin_entry(data: dict[str, Any], info: CcxInfo) -> dict[str, Any]:
    """Add or update a plugin entry in the data dict.

    Removes any existing entry with the same pluginId, then appends
    the new one.  Returns a new dict (does not mutate the original).

    Args:
        data: The parsed PS.json data (from read_psjson()).
        info: Parsed plugin metadata.

    Returns:
        A new data dict with the plugin added.
    """
    new_entry = build_psjson_entry(
        plugin_id=info.plugin_id,
        name=info.name,
        version=info.version,
        host_min_version=info.host_min_version,
    )

    plugins = [
        p for p in data.get("plugins", []) if p.get("pluginId") != info.plugin_id
    ]
    plugins.append(new_entry)

    return {"plugins": plugins}


def remove_plugin_entry(data: dict[str, Any], plugin_id: str) -> dict[str, Any]:
    """Remove a plugin entry from the data dict by pluginId.

    Args:
        data: The parsed PS.json data.
        plugin_id: The plugin ID to remove.

    Returns:
        A new data dict without the removed plugin.

    Raises:
        PluginNotFoundError: If the plugin_id is not found in the data.
    """
    plugins = data.get("plugins", [])
    new_plugins = [p for p in plugins if p.get("pluginId") != plugin_id]

    if len(new_plugins) == len(plugins):
        raise PluginNotFoundError(f"Plugin '{plugin_id}' not found in PS.json.")

    return {"plugins": new_plugins}


# Retry settings for write_psjson_with_retry
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1.0


def write_psjson_with_retry(data: dict[str, Any]) -> None:
    """Write PS.json with retry logic for transient locks.

    Photoshop may hold a brief lock on PS.json at startup.  This function
    retries up to MAX_RETRIES times with a delay before giving up.

    Args:
        data: The full PS.json data dict to write.

    Raises:
        PermissionError: If all retries fail due to permission issues.
    """
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            write_psjson(data)
            return
        except (PermissionError, OSError) as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)

    raise PermissionError(
        f"Could not write to PS.json after {MAX_RETRIES} attempts.\n"
        "Please close Adobe Photoshop and try again."
    ) from last_error
