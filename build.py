#!/usr/bin/env python3
"""
Build script: packages the CCX Plugin Installer into a single .exe using PyInstaller.

Usage:
    python build.py              # Build the exe
    python build.py --clean      # Clean build (remove build/dist first)

Output:
    dist/CCX Plugin Installer.exe    (single-file Windows executable)
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "CCX Installer.spec"
ENTRY_SCRIPT = PROJECT_ROOT / "run.py"
ICON_FILE = PROJECT_ROOT / "assets" / "icon.ico"
APP_NAME = "CCX Plugin Installer"


def clean() -> None:
    """Remove previous build artifacts."""
    for path in (DIST_DIR, BUILD_DIR, SPEC_FILE):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.is_file():
            path.unlink()
    print("[CLEAN] Removed previous build artifacts.")


def build() -> None:
    """Run PyInstaller to produce a single-file Windows executable."""
    # Build the command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",                 # No console window
        "--name", APP_NAME,
        "--clean",
        "--noconfirm",
    ]

    # Add icon if it exists
    if ICON_FILE.exists():
        cmd.extend(["--icon", str(ICON_FILE)])
        # Also bundle the icon so the app can use it at runtime if needed
        cmd.extend(["--add-data", f"{ICON_FILE};assets"])
    else:
        print("[WARNING] No icon.ico found in assets/.  Building without custom icon.")
        print("          Run 'python generate_icon.py' to create one.")

    # Entry point
    cmd.append(str(ENTRY_SCRIPT))

    print(f"[BUILD] Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))

    if result.returncode == 0:
        print()
        print("=" * 60)
        exe_path = DIST_DIR / f"{APP_NAME}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✓ Build successful!")
            print(f"  Output: {exe_path}")
            print(f"  Size:   {size_mb:.1f} MB")
        print("=" * 60)
    else:
        print()
        print("✗ Build failed! Check the output above for errors.")
        sys.exit(result.returncode)


def main() -> None:
    clean_flag = "--clean" in sys.argv

    if clean_flag:
        clean()

    print(f"[BUILD] Packaging {APP_NAME}...")
    print()

    # Verify dependencies
    print("[CHECK] Verifying dependencies...")
    try:
        import customtkinter
        print(f"  customtkinter {customtkinter.__version__}")
    except ImportError:
        print("  ✗ customtkinter not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    try:
        from PIL import Image
        print(f"  Pillow {Image.__version__}")
    except ImportError:
        print("  ✗ Pillow not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    print()

    build()


if __name__ == "__main__":
    main()
