"""
CCX file parser — validate, read manifest, and extract .ccx archives.

A .ccx file is a standard ZIP archive with a .ccx extension containing
a UXP plugin (manifest.json, index.html, assets/, icons/, etc.).
"""

import json
import os
import zipfile
from dataclasses import dataclass, field
from typing import Any

from ..utils.tempdir import temp_work_dir
from ..utils.validation import validate_manifest


@dataclass
class CcxInfo:
    """Immutable data class holding parsed plugin metadata from a .ccx file."""

    plugin_id: str
    name: str
    version: str
    host_app: str = "unknown"
    host_min_version: str = "22.5.0"
    main_file: str = "index.html"
    manifest_version: int = 0
    entrypoints: list[dict[str, Any]] = field(default_factory=list)
    panel_labels: list[str] = field(default_factory=list)

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> "CcxInfo":
        """Build a CcxInfo from a parsed manifest.json dict."""
        host = manifest.get("host", {})
        if isinstance(host, list) and len(host) > 0:
            host = host[0]
        if not isinstance(host, dict):
            host = {}

        entrypoints: list[dict[str, Any]] = manifest.get("entrypoints", [])
        panel_labels: list[str] = []
        for ep in entrypoints:
            label = ep.get("label", {})
            if isinstance(label, dict):
                label_text = label.get("default", "")
            else:
                label_text = str(label)
            if label_text:
                panel_labels.append(label_text)

        return cls(
            plugin_id=manifest.get("id", ""),
            name=manifest.get("name", "Unknown Plugin"),
            version=manifest.get("version", "0.0.0"),
            host_app=host.get("app", "unknown"),
            host_min_version=host.get("minVersion", "22.5.0"),
            main_file=manifest.get("main", "index.html"),
            manifest_version=manifest.get("manifestVersion", 0),
            entrypoints=entrypoints,
            panel_labels=panel_labels,
        )


class CcxParseError(Exception):
    """Raised when a .ccx file cannot be parsed or has invalid content."""

    def __init__(self, message: str, detail: str | None = None):
        super().__init__(message)
        self.detail = detail


def parse_ccx(ccx_path: str) -> CcxInfo:
    """Open a .ccx file as ZIP, locate and parse manifest.json.

    This performs a lightweight parse — only manifest.json is extracted
    to a temp directory.  Use extract_ccx() for full extraction.

    Args:
        ccx_path: Path to the .ccx file.

    Returns:
        CcxInfo with parsed plugin metadata.

    Raises:
        CcxParseError: If the file is not a valid ZIP, has no manifest.json,
                       or the manifest is malformed.
    """
    if not os.path.isfile(ccx_path):
        raise CcxParseError(f"File not found: {ccx_path}")

    if not zipfile.is_zipfile(ccx_path):
        raise CcxParseError(
            "The selected file is not a valid .ccx plugin.\n"
            ".ccx files are ZIP archives containing a UXP plugin."
        )

    try:
        with zipfile.ZipFile(ccx_path, "r") as zf:
            # Locate manifest.json — it should be at the root
            manifest_candidates = [
                name
                for name in zf.namelist()
                if name.rstrip("/").endswith("manifest.json")
            ]
            # Prefer one at the top level
            manifest_name = None
            for candidate in manifest_candidates:
                if "/" not in candidate.rstrip("/").rsplit("/", 1)[0] or candidate in (
                    "manifest.json",
                    "./manifest.json",
                ):
                    manifest_name = candidate
                    break
            if not manifest_name and manifest_candidates:
                manifest_name = manifest_candidates[0]

            if not manifest_name:
                raise CcxParseError(
                    "No manifest.json found in the .ccx file.\n"
                    "This file may be corrupted or not a valid plugin package."
                )

            # Security: check for Zip Slip path traversal
            _check_zip_slip(zf)

            # Extract manifest.json to a temp dir for reading
            with temp_work_dir() as tmp:
                zf.extract(manifest_name, tmp)
                manifest_path = os.path.join(tmp, manifest_name)
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

    except zipfile.BadZipFile as e:
        raise CcxParseError("The .ccx file is corrupted (invalid ZIP).", str(e)) from e
    except json.JSONDecodeError as e:
        raise CcxParseError(
            f"manifest.json is not valid JSON:\n"
            f"Line {e.lineno}, column {e.colno}: {e.msg}"
        ) from e

    # Validate required fields
    warnings = validate_manifest(manifest)
    if any(not w.startswith("No 'host'") for w in warnings):
        # Only treat non-host warnings as hard errors
        hard_warnings = [w for w in warnings if "host" not in w.lower()]
        if hard_warnings:
            raise CcxParseError(
                "manifest.json is missing required fields:\n"
                + "\n".join(f"  • {w}" for w in hard_warnings)
            )

    return CcxInfo.from_manifest(manifest)


def extract_ccx(ccx_path: str, dest_dir: str) -> None:
    """Fully extract a .ccx archive into dest_dir.

    Creates dest_dir if it does not exist.  Includes Zip Slip protection.

    Args:
        ccx_path: Path to the .ccx file.
        dest_dir: Directory to extract into.

    Raises:
        CcxParseError: On invalid .ccx or Zip Slip detection.
        OSError: On disk full, permission denied, etc.
    """
    if not zipfile.is_zipfile(ccx_path):
        raise CcxParseError("The selected file is not a valid .ccx plugin.")

    os.makedirs(dest_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(ccx_path, "r") as zf:
            _check_zip_slip(zf)
            zf.extractall(dest_dir)
    except zipfile.BadZipFile as e:
        raise CcxParseError("The .ccx file is corrupted (invalid ZIP).", str(e)) from e


def _check_zip_slip(zf: zipfile.ZipFile) -> None:
    """Check all entries in the ZIP for path-traversal (Zip Slip) attacks.

    Raises CcxParseError if any entry has '..' components.
    """
    for member in zf.infolist():
        # Normalize the path to catch encoded traversal attempts
        normalized = os.path.normpath(member.filename)
        if normalized.startswith("..") or os.path.isabs(normalized):
            raise CcxParseError(
                f"Security: The .ccx file contains an unsafe path: '{member.filename}'.\n"
                "This plugin may be malicious."
            )
