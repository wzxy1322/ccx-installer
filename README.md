# 📦 CCX格式插件安装器 CCX Plugin Installer

无需Creative Cloud安装 Adobe Photoshop `.ccx` (UXP) 插件

A modern Windows GUI tool for installing Adobe Photoshop `.ccx` (UXP) plugins.
No Creative Cloud Desktop required — install plugins directly with a clean graphical interface.

## 🚀 安装

### 从源码安装 Run from Source

```bash
# Clone the repo
git clone https://github.com/yourusername/ccx-installer-gui.git
cd ccx-installer-gui

# Install dependencies
pip install -r requirements.txt

# Run
python run.py
```

### 构建.exe文件 Build Your Own .exe

```bash
# Generate an icon (optional)
python generate_icon.py

# Build the single-file executable
python build.py

# Output: dist/CCX Plugin Installer.exe
```

## ⚠️ Important Notes

- **Always restart Photoshop** after installing or uninstalling a plugin — Photoshop reads the plugin registry only at startup.
- The tool installs to the **UXP External** directory (`%APPDATA%\Adobe\UXP\Plugins\External\`). Plugins installed this way are "unmanaged" — they won't appear in Creative Cloud Desktop's "Manage Plugins" panel, but they work identically.
- On first run, Windows SmartScreen may warn about the unsigned `.exe`. This is normal for community-built tools.

## 📄 License

MIT License — see [LICENSE](LICENSE) file.
