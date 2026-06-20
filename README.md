# 📦 CCX Plugin Installer

用于安装 Adobe Photoshop `.ccx` (UXP) 插件
无需Creative Cloud，通过简洁的图形界面直接安装插件

A modern Windows GUI tool for installing Adobe Photoshop `.ccx` (UXP) plugins.
No Creative Cloud Desktop required — install plugins directly with a clean graphical interface.

## 🚀 Quick Start

### Run from Source

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
