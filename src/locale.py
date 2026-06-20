"""
多语言文本管理 (i18n).

模块级 L 实例可直接 `from ..locale import L` 然后 `L.t("key")` 获取当前语言文本。
切换语言: `L.toggle()` → 自动通知所有注册的刷新回调。
注册回调: `L.on_switch(callback)` — callback 无参数，用于刷新 UI。
"""

from __future__ import annotations
from typing import Callable


# ── 英文文本库 ──────────────────────────────────────────────────
_EN: dict[str, str] = {
    # 主窗口
    "app.title": "📦  CCX Plugin Installer",
    "app.subtitle": "Adobe Photoshop UXP Plugin Manager",
    "app.tab.install": "Install Plugin",
    "app.tab.manage": "Manage Installed",
    "app.status.ready": "Ready",
    "app.lang.btn": "中",
    "app.lang.tip": "Switch to Chinese",
    # 安装标签页
    "install.select.label": "Select Plugin",
    "install.path.placeholder": "Choose a .ccx file...",
    "install.browse.btn": "Browse...",
    "install.drop.label": "📂  Drop your .ccx file here\nor click Browse above",
    "install.info.heading": "Plugin Details",
    "install.info.field.name": "Name",
    "install.info.field.id": "ID",
    "install.info.field.version": "Version",
    "install.info.field.host": "Host",
    "install.info.field.panels": "Panels",
    "install.info.na": "—",
    "install.btn.default": "Install Plugin",
    "install.btn.reinstall": "Reinstall Plugin (same version)",
    "install.btn.update": "Update from v{old} to v{new}",
    "install.btn.installing": "Installing...",
    "install.btn.installed": "Installed ✓",
    "install.status.label": "Status",
    "install.dialog.title": "Select a Photoshop CCX Plugin",
    "install.dialog.filetype": "CCX Plugin",
    # 安装状态
    "install.status.loading": "Loading: {filename}",
    "install.status.valid": "Plugin manifest valid.",
    "install.status.drop_ccx": "Dropped file is not a .ccx plugin.",
    "install.status.file_not_found": "File not found: {path}",
    "install.status.note_installed": "Note: Version {version} is already installed.",
    "install.status.found_old": "Found existing v{old} — will be replaced.",
    # 安装对话框
    "dialog.invalid_ccx": "Invalid .ccx File",
    "dialog.no_plugin.title": "No Plugin Selected",
    "dialog.no_plugin.msg": "Please select a .ccx file first.",
    "dialog.non_ps.title": "Non-Photoshop Plugin",
    "dialog.non_ps.msg": "This plugin targets '{app}', not Photoshop (PS).\n\nIt may not work correctly in Photoshop.\n\nContinue anyway?",
    "dialog.reinstall.title": "Reinstall Plugin?",
    "dialog.reinstall.msg": "Version {version} is already installed.\n\nReinstall to overwrite?",
    "dialog.update.title": "Update Plugin?",
    "dialog.update.msg": "This will replace version {old} with {new}.\n\nContinue?",
    "dialog.install_success.title": "Installation Complete",
    "dialog.install_success.msg": "{name} v{version} has been installed.\n\nPlease restart Adobe Photoshop to load the plugin.",
    "dialog.install_failed.title": "Installation Failed",
    # 安装进度
    "install.progress.removing": "Removing old versions...",
    "install.progress.preparing": "Preparing plugin directory...",
    "install.progress.extracting": "Extracting plugin files to External\\{folder}...",
    "install.progress.registering": "Registering in PS.json...",
    "install.progress.complete": "Installation complete.",
    "install.success_status": "✓ {name} v{version} installed successfully!",
    "install.restart_warning": "⚠ Please RESTART Adobe Photoshop to load the plugin.",
    "install.failed_status": "✗ Installation failed: {error}",
    # 管理标签页
    "manage.heading": "Installed UXP Plugins",
    "manage.refresh.btn": "↻ Refresh List",
    "manage.empty": "No plugins installed.\n\nUse the \"Install Plugin\" tab to install a .ccx file.",
    "manage.found_count": "Found {count} plugin(s).",
    "manage.status.uninstalling": "Uninstalling...",
    "manage.status.uninstall_failed": "Uninstall failed.",
    "manage.btn.uninstall": "Uninstall",
    "manage.btn.remove_entry": "Remove Entry",
    "manage.btn.register": "Register",
    "manage.status.label": "Status: {status}",
    "manage.status.enabled": "Enabled",
    "manage.status.disabled": "Disabled",
    "manage.status.unregistered": "Unregistered — no PS.json entry",
    "manage.status.missing": "Missing files — only in PS.json",
    # 卸载对话框
    "dialog.uninstall.title": "Uninstall Plugin?",
    "dialog.uninstall.msg": "Are you sure you want to remove:\n\n  {name}\n  Version: {version}\n  ID: {plugin_id}\n\nThis cannot be undone.",
    "dialog.uninstall_success.title": "Uninstalled",
    "dialog.uninstall_success.msg": "{name} has been removed.\n\nPlease restart Photoshop if it was running.",
    "dialog.uninstall_failed.title": "Uninstall Failed",
    "manage.uninstall_success": "✓ {name} has been uninstalled.",
    # 注册对话框
    "dialog.register_success.title": "Registered",
    "dialog.register_success.msg": "{name} has been registered.\n\nPlease restart Photoshop.",
    "dialog.register_failed.title": "Registration Failed",
    "manage.register_success": "✓ {name} registered in PS.json.",
    # 删除条目对话框
    "dialog.remove_entry.title": "Remove Stale Entry?",
    "dialog.remove_entry.msg": "Remove the PS.json entry for:\n\n  {name}\n  ID: {plugin_id}\n\nThe plugin files are already missing.",
    "manage.remove_entry_success": "✓ Stale entry for {name} removed.",
    "manage.entry_already_removed": "Entry already removed.",
    # 对话框按钮
    "btn.yes": "Yes",
    "btn.no": "No",
    "btn.ok": "OK",
    "btn.continue": "Continue",
    "btn.cancel": "Cancel",
    # 通用
    "gen.plugin_fallback": "Plugin",
    "gen.unexpected_error": "Unexpected error",
    "gen.restart_warning": "⚠ Please RESTART Adobe Photoshop to load the plugin.",
}

# ── 中文文本库 ──────────────────────────────────────────────────
_ZH: dict[str, str] = {
    "app.title": "📦  CCX 插件安装器",
    "app.subtitle": "Adobe Photoshop UXP 插件管理工具",
    "app.tab.install": "安装插件",
    "app.tab.manage": "已安装管理",
    "app.status.ready": "就绪",
    "app.lang.btn": "EN",
    "app.lang.tip": "切换到英文",
    "install.select.label": "选择插件",
    "install.path.placeholder": "选择 .ccx 文件...",
    "install.browse.btn": "浏览...",
    "install.drop.label": "📂  将 .ccx 文件拖拽到此处\n或点击上方「浏览」按钮",
    "install.info.heading": "插件详情",
    "install.info.field.name": "名称",
    "install.info.field.id": "ID",
    "install.info.field.version": "版本",
    "install.info.field.host": "宿主",
    "install.info.field.panels": "面板",
    "install.info.na": "—",
    "install.btn.default": "安装插件",
    "install.btn.reinstall": "重新安装插件（相同版本）",
    "install.btn.update": "从 v{old} 更新到 v{new}",
    "install.btn.installing": "正在安装...",
    "install.btn.installed": "已安装 ✓",
    "install.status.label": "状态",
    "install.dialog.title": "选择 Photoshop CCX 插件",
    "install.dialog.filetype": "CCX 插件",
    "install.status.loading": "正在加载: {filename}",
    "install.status.valid": "插件清单验证通过。",
    "install.status.drop_ccx": "拖入的文件不是 .ccx 插件。",
    "install.status.file_not_found": "文件未找到: {path}",
    "install.status.note_installed": "提示: 版本 {version} 已安装。",
    "install.status.found_old": "发现旧版本 v{old} — 将被替换。",
    "dialog.invalid_ccx": "无效的 .ccx 文件",
    "dialog.no_plugin.title": "未选择插件",
    "dialog.no_plugin.msg": "请先选择一个 .ccx 文件。",
    "dialog.non_ps.title": "非 Photoshop 插件",
    "dialog.non_ps.msg": "此插件目标宿主为「{app}」，而非 Photoshop (PS)。\n\n在 Photoshop 中可能无法正常运行。\n\n确定要继续安装吗？",
    "dialog.reinstall.title": "重新安装插件？",
    "dialog.reinstall.msg": "版本 {version} 已经安装。\n\n是否覆盖重新安装？",
    "dialog.update.title": "更新插件？",
    "dialog.update.msg": "将把版本 {old} 替换为 {new}。\n\n确定继续？",
    "dialog.install_success.title": "安装完成",
    "dialog.install_success.msg": "{name} v{version} 已安装。\n\n请重启 Adobe Photoshop 以加载插件。",
    "dialog.install_failed.title": "安装失败",
    "install.progress.removing": "正在清理旧版本...",
    "install.progress.preparing": "正在准备插件目录...",
    "install.progress.extracting": "正在解压插件文件到 External\\{folder}...",
    "install.progress.registering": "正在注册到 PS.json...",
    "install.progress.complete": "安装完成。",
    "install.success_status": "✓ {name} v{version} 安装成功！",
    "install.restart_warning": "⚠ 请重启 Adobe Photoshop 以加载插件。",
    "install.failed_status": "✗ 安装失败: {error}",
    "manage.heading": "已安装的 UXP 插件",
    "manage.refresh.btn": "↻ 刷新列表",
    "manage.empty": "暂无已安装插件。\n\n请使用「安装插件」标签页安装 .ccx 文件。",
    "manage.found_count": "找到 {count} 个插件。",
    "manage.status.uninstalling": "正在卸载...",
    "manage.status.uninstall_failed": "卸载失败。",
    "manage.btn.uninstall": "卸载",
    "manage.btn.remove_entry": "删除条目",
    "manage.btn.register": "注册",
    "manage.status.label": "状态: {status}",
    "manage.status.enabled": "已启用",
    "manage.status.disabled": "已禁用",
    "manage.status.unregistered": "未注册 — 缺少 PS.json 条目",
    "manage.status.missing": "文件缺失 — 仅存 PS.json 条目",
    "dialog.uninstall.title": "卸载插件？",
    "dialog.uninstall.msg": "确定要移除以下插件吗？\n\n  {name}\n  版本: {version}\n  ID: {plugin_id}\n\n此操作不可撤销。",
    "dialog.uninstall_success.title": "已卸载",
    "dialog.uninstall_success.msg": "{name} 已移除。\n\n如果 Photoshop 正在运行，请重启。",
    "dialog.uninstall_failed.title": "卸载失败",
    "manage.uninstall_success": "✓ {name} 已卸载。",
    "dialog.register_success.title": "已注册",
    "dialog.register_success.msg": "{name} 已注册到 PS.json。\n\n请重启 Photoshop。",
    "dialog.register_failed.title": "注册失败",
    "manage.register_success": "✓ {name} 已注册到 PS.json。",
    "dialog.remove_entry.title": "删除残留条目？",
    "dialog.remove_entry.msg": "删除以下插件的 PS.json 条目？\n\n  {name}\n  ID: {plugin_id}\n\n插件文件已不存在。",
    "manage.remove_entry_success": "✓ {name} 的残留条目已删除。",
    "manage.entry_already_removed": "条目已不存在。",
    "btn.yes": "是",
    "btn.no": "否",
    "btn.ok": "确定",
    "btn.continue": "继续",
    "btn.cancel": "取消",
    "gen.plugin_fallback": "插件",
    "gen.unexpected_error": "未知错误",
    "gen.restart_warning": "⚠ 请重启 Adobe Photoshop 以加载插件。",
}


class LocaleManager:
    """多语言管理器 — 模块级单例。"""

    _current: str = "zh"
    _observers: list[Callable[[], None]] = []

    # ── 公开 API ────────────────────────────────────────────────

    @classmethod
    def t(cls, key: str, **fmt) -> str:
        """获取当前语言的文本。支持 {param} 格式化。

        Usage:
            L.t("install.btn.update", old="1.0", new="2.0")
        """
        strings = _ZH if cls._current == "zh" else _EN
        text = strings.get(key, key)
        if fmt:
            text = text.format(**fmt)
        return text

    @classmethod
    @property
    def lang(cls) -> str:
        """当前语言代码: "zh" | "en"."""
        return cls._current

    @classmethod
    def toggle(cls) -> None:
        """切换语言并通知所有观察者刷新。"""
        cls._current = "en" if cls._current == "zh" else "zh"
        for cb in cls._observers:
            cb()

    @classmethod
    def on_switch(cls, callback: Callable[[], None]) -> None:
        """注册语言切换回调（无参数）。"""
        if callback not in cls._observers:
            cls._observers.append(callback)

    @classmethod
    def remove_observer(cls, callback: Callable[[], None]) -> None:
        """移除观察者。"""
        if callback in cls._observers:
            cls._observers.remove(callback)


# 模块级别名，方便导入
L = LocaleManager

# ── 向后兼容: 暴露常用键作为模块属性（供非 GUI 代码快速访问）──
BTN_YES = "btn.yes"
BTN_NO = "btn.no"
BTN_OK = "btn.ok"
BTN_CONTINUE = "btn.continue"
BTN_CANCEL = "btn.cancel"
