"""
Manifest.json validation helpers.
"""

from typing import Any


# Required top-level fields in a UXP manifest.json (v4/v5/v6)
REQUIRED_FIELDS = ["id", "name", "version", "main"]


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Check that a manifest dict has all required fields.

    Returns a list of human-readable warning/error strings.
    An empty list means the manifest is valid.

    Args:
        manifest: The parsed manifest.json as a dict.

    Returns:
        A list of validation messages (empty = valid).
    """
    warnings: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in manifest or not manifest[field]:
            warnings.append(f"Missing required field: '{field}'")

    # Host info is optional in newer manifest versions but helpful to have
    host = manifest.get("host")
    if host is None:
        warnings.append("No 'host' block found — cannot verify host application.")
    elif isinstance(host, dict):
        if "app" not in host:
            warnings.append("Host block missing 'app' field.")
    elif isinstance(host, list):
        # Some manifests use an array of hosts
        if not host:
            warnings.append("Host array is empty.")
        else:
            for i, h in enumerate(host):
                if "app" not in h:
                    warnings.append(f"Host[{i}] missing 'app' field.")
    else:
        warnings.append(f"Unexpected 'host' type: {type(host).__name__}")

    # Entrypoints are optional at validation level but useful for display
    entrypoints = manifest.get("entrypoints")
    if not entrypoints:
        warnings.append("No 'entrypoints' defined — plugin may have no UI panels.")

    return warnings


def is_valid_plugin_id(plugin_id: str) -> bool:
    """Check if a plugin ID looks valid (non-empty string)."""
    return bool(plugin_id) and isinstance(plugin_id, str) and len(plugin_id) > 0


def is_valid_version(version: str) -> bool:
    """Loosely check if a version string looks like semver (digits separated by dots)."""
    if not version or not isinstance(version, str):
        return False
    parts = version.split(".")
    return all(p.isdigit() for p in parts if p)
