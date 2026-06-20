# 📦 CCX Plugin Installer

A modern Windows GUI tool for installing Adobe Photoshop `.ccx` (UXP) plugins.

No Creative Cloud Desktop required — install plugins directly with a clean graphical interface.

## ✨ Features

- **Browse & Parse** — Select a `.ccx` file and instantly view plugin details (name, version, ID, panels, host requirements)
- **One-Click Install** — Extracts the plugin, copies to the correct UXP directory, and registers it in Photoshop's plugin registry
- **Manage Installed** — View all installed plugins, check their status, and uninstall with a single click
- **Smart Detection** — Detects existing installations, offers update/reinstall flow, and warns about non-Photoshop plugins
- **Repair Tools** — Handles edge cases like unregistered plugins or stale PS.json entries
- **No Dependencies on Adobe Tools** — Works offline with pure filesystem operations

## 🚀 Quick Start

### Prerequisites
- **Windows 10 or later**
- **Adobe Photoshop 2022 or later** (v23.0.0+)
- No Python required for the `.exe` release

### Option A: Download Pre-built .exe

1. Download `CCX Plugin Installer.exe` from [Releases](https://github.com/yourusername/ccx-installer-gui/releases)
2. Run the `.exe` (Windows may show SmartScreen warning — click "More Info" → "Run Anyway")
3. Browse to your `.ccx` file and click **Install Plugin**
4. Restart Photoshop

### Option B: Run from Source

```bash
# Clone the repo
git clone https://github.com/yourusername/ccx-installer-gui.git
cd ccx-installer-gui

# Install dependencies
pip install -r requirements.txt

# Run
python run.py
```

### Build Your Own .exe

```bash
# Generate an icon (optional)
python generate_icon.py

# Build the single-file executable
python build.py

# Output: dist/CCX Plugin Installer.exe
```

## 🔧 How It Works

1. **`.ccx` = ZIP** — The tool opens the `.ccx` file as a ZIP archive, extracts `manifest.json`, and displays plugin metadata.

2. **Install** — The plugin is extracted to `%APPDATA%\Adobe\UXP\Plugins\External\{pluginId}_{version}\` and registered in `%APPDATA%\Adobe\UXP\PluginsInfo\v1\PS.json`.

3. **No Adobe Dependencies** — Unlike the official UPIA installer, this tool works without Creative Cloud Desktop. It directly manipulates the filesystem paths that Photoshop reads at startup.

4. **Atomic PS.json Writes** — PS.json (the plugin registry) is written via a `.tmp` file + `os.replace()` to prevent corruption.

5. **Background Threading** — Install/uninstall operations run in background threads, keeping the UI responsive with live status updates.

## ⚠️ Important Notes

- **Always restart Photoshop** after installing or uninstalling a plugin — Photoshop reads the plugin registry only at startup.
- The tool installs to the **UXP External** directory (`%APPDATA%\Adobe\UXP\Plugins\External\`). Plugins installed this way are "unmanaged" — they won't appear in Creative Cloud Desktop's "Manage Plugins" panel, but they work identically.
- **Security**: The tool checks for [Zip Slip](https://snyk.io/research/zip-slip-vulnerability) path-traversal attacks when extracting `.ccx` files.
- On first run, Windows SmartScreen may warn about the unsigned `.exe`. This is normal for community-built tools.

## 📄 License

MIT License — see [LICENSE](LICENSE) file.
