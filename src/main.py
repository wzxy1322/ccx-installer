"""
Entry point for the CCX Plugin Installer.

Launches a customtkinter GUI application for installing and managing
Adobe Photoshop .ccx (UXP) plugins.

Drag-and-drop support is enabled by patching tkinter.Tk with
tkinterdnd2.TkinterDnD.Tk before the CTk root window is created.
"""

import sys
import os

# Ensure the src package is importable when running as a bundled exe
if getattr(sys, "frozen", False):
    # Running as PyInstaller bundle
    _bundle_dir = os.path.dirname(sys.executable)
else:
    _bundle_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _bundle_dir not in sys.path:
    sys.path.insert(0, _bundle_dir)

# ── Enable drag-and-drop support ───────────────────────────────
# Replace tkinter.Tk with a DnD-aware Tk so that customtkinter.CTk
# (which inherits from tkinter.Tk) gets WM_DROPFILES support on Windows
# and child widgets can register as drop targets.
#
# We must save the ORIGINAL Tk.__init__ BEFORE importing tkinterdnd2,
# because TkinterDnD.Tk.__init__ internally calls tkinter.Tk.__init__.
# After we replace tkinter.Tk, that internal call would recurse infinitely.
# Our _DnDTk wrapper calls the saved original init directly to break the loop.
import tkinter as _tk
_ORIG_Tk_init = _tk.Tk.__init__

from tkinterdnd2 import TkinterDnD

class _DnDTk(TkinterDnD.Tk):
    """DnD-aware Tk that delegates to the real tkinter.Tk.__init__."""
    def __init__(self, *args, **kw):
        _ORIG_Tk_init(self, *args, **kw)
        self.TkdndVersion = TkinterDnD._require(self)

_tk.Tk = _DnDTk

import customtkinter as ctk

from .gui.app import CcxInstallerApp
from .gui.styles import ACCENT_BLUE, BG_DARK, TEXT_PRIMARY


def main() -> None:
    """Configure theming and launch the application."""
    # Theme configuration
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Optionally set a custom color theme
    try:
        ctk.ThemeManager.theme["CTkButton"]["fg_color"] = ACCENT_BLUE
        ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = BG_DARK
    except (KeyError, AttributeError):
        pass

    app = CcxInstallerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
