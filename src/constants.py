"""
Path constants and JSON templates for the CCX Plugin Installer.
"""

import os

# ---- UXP Plugin Paths ----
UXP_EXTERNAL_PATH = os.path.expanduser(
    r"~\AppData\Roaming\Adobe\UXP\Plugins\External"
)
UXP_PLUGINS_INFO_PATH = os.path.expanduser(
    r"~\AppData\Roaming\Adobe\UXP\PluginsInfo\v1"
)
PS_JSON_PATH = os.path.join(UXP_PLUGINS_INFO_PATH, "PS.json")

# ---- Default Values ----
HOST_MIN_VERSION = "22.5.0"
PLUGIN_TYPE = "uxp"
PLUGIN_STATUS = "enabled"

# ---- App Metadata ----
APP_TITLE = "CCX Plugin Installer"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 650
WINDOW_MIN_WIDTH = 750
WINDOW_MIN_HEIGHT = 500

# ---- Logging ----
LOG_FILE = os.path.join(os.environ.get("TEMP", os.path.expanduser("~")), "ccx_installer.log")


def build_psjson_entry(
    plugin_id: str,
    name: str,
    version: str,
    host_min_version: str = HOST_MIN_VERSION,
) -> dict:
    """Build a single plugin entry for PS.json from manifest fields.

    The path uses $localPlugins which UXP resolves to
    %APPDATA%\\Adobe\\UXP\\Plugins at runtime.
    """
    folder_name = f"{plugin_id}_{version}"
    return {
        "hostMinVersion": host_min_version,
        "name": name,
        "path": f"$localPlugins\\External\\{folder_name}",
        "pluginId": plugin_id,
        "status": PLUGIN_STATUS,
        "type": PLUGIN_TYPE,
        "versionString": version,
    }
