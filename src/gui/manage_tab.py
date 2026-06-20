"""
管理标签页 — 已安装插件列表、卸载、注册修复。
支持 L.toggle() 中英文切换。
"""

import threading

import customtkinter as ctk

from ..core.scanner import InstalledPlugin, scan_installed_plugins
from ..core.uninstaller import UninstallError, uninstall_plugin
from ..locale import L
from .dialogs import show_confirm_dialog, show_error_dialog, show_success_dialog
from .styles import (
    ACCENT_BLUE,
    ACCENT_BLUE_HOVER,
    BODY_FONT,
    BUTTON_HEIGHT,
    DANGER_RED,
    DANGER_RED_HOVER,
    ERROR_RED,
    PADDING_LARGE,
    PADDING_SMALL,
    PADDING_STANDARD,
    PADDING_XL,
    SMALL_FONT,
    SUBHEADING_FONT,
    SUCCESS_GREEN,
    TEXT_MUTED,
    TEXT_PRIMARY,
    WARNING_ORANGE,
)


class ManageTab(ctk.CTkFrame):
    """「已安装管理」标签页。"""

    def __init__(self, master):
        super().__init__(master)
        self._installed_plugins: list[InstalledPlugin] = []
        self._plugin_rows: list[ctk.CTkFrame] = []

        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 头部
        self._header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._header_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_XL, pady=(PADDING_XL, PADDING_SMALL))
        self._header_frame.grid_columnconfigure(0, weight=1)

        self._heading_label = ctk.CTkLabel(
            self._header_frame,
            text=L.t("manage.heading"),
            font=SUBHEADING_FONT,
            text_color=TEXT_PRIMARY,
        )
        self._heading_label.grid(row=0, column=0, sticky="w")

        self._refresh_btn = ctk.CTkButton(
            self._header_frame,
            text=L.t("manage.refresh.btn"),
            font=BODY_FONT,
            fg_color="transparent",
            border_width=1,
            border_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            width=140,
            height=BUTTON_HEIGHT,
            command=self.refresh,
        )
        self._refresh_btn.grid(row=0, column=1, sticky="e")

        # 可滚动插件列表
        self._list_container = ctk.CTkScrollableFrame(self)
        self._list_container.grid(row=1, column=0, sticky="nsew", padx=PADDING_XL, pady=PADDING_STANDARD)
        self._list_container.grid_columnconfigure(0, weight=1)

        self._empty_label = ctk.CTkLabel(
            self._list_container,
            text=L.t("manage.empty"),
            font=BODY_FONT,
            text_color=TEXT_MUTED,
            justify="center",
        )

        # 状态标签
        self._status_label = ctk.CTkLabel(
            self,
            text="",
            font=SMALL_FONT,
            text_color=TEXT_MUTED,
        )
        self._status_label.grid(row=2, column=0, sticky="w", padx=PADDING_XL, pady=(PADDING_SMALL, PADDING_SMALL))

    # ── 语言刷新 ──────────────────────────────────────────────────

    def _refresh_language(self) -> None:
        """语言切换时刷新所有静态文本。"""
        self._heading_label.configure(text=L.t("manage.heading"))
        self._refresh_btn.configure(text=L.t("manage.refresh.btn"))
        self._empty_label.configure(text=L.t("manage.empty"))
        # 刷新列表行和状态文字
        self._rebuild_list()
        # 刷新找到数量
        count = len(self._installed_plugins)
        self._status_label.configure(text=L.t("manage.found_count", count=count))

    # ── 公开接口 ──────────────────────────────────────────────────

    def refresh(self) -> None:
        """重新扫描并重建插件列表。"""
        self._installed_plugins = scan_installed_plugins()
        self._rebuild_list()
        count = len(self._installed_plugins)
        self._status_label.configure(text=L.t("manage.found_count", count=count))

    # ── 列表管理 ──────────────────────────────────────────────────

    def _rebuild_list(self) -> None:
        """清空并重建插件列表。"""
        for row in self._plugin_rows:
            row.destroy()
        self._plugin_rows.clear()

        if not self._installed_plugins:
            self._empty_label.configure(text=L.t("manage.empty"))
            self._empty_label.grid(row=0, column=0, pady=40, padx=20, sticky="ew")
        else:
            self._empty_label.grid_remove()
            for i, plugin in enumerate(self._installed_plugins):
                row = self._build_plugin_row(plugin, i)
                row.grid(row=i, column=0, sticky="ew", pady=(0, PADDING_SMALL))
                self._plugin_rows.append(row)

    def _build_plugin_row(self, plugin: InstalledPlugin, index: int) -> ctk.CTkFrame:
        """构建单个插件行。"""
        row_frame = ctk.CTkFrame(self._list_container)
        row_frame.grid_columnconfigure(0, weight=1)

        icon_label = ctk.CTkLabel(
            row_frame,
            text="📦",
            font=("Segoe UI", 24),
        )
        icon_label.grid(row=0, column=0, rowspan=3, padx=(PADDING_LARGE, PADDING_STANDARD), pady=PADDING_STANDARD, sticky="n")

        # 名称 + 版本
        name_label = ctk.CTkLabel(
            row_frame,
            text=f"{plugin.name}  v{plugin.version}",
            font=BODY_FONT,
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        name_label.grid(row=0, column=1, sticky="w", pady=(PADDING_STANDARD, 0))

        # ID + 路径
        detail_parts = [f"ID: {plugin.plugin_id}"]
        if plugin.install_path:
            detail_parts.append(f"  •  {plugin.install_path}")
        detail_text = "".join(detail_parts)

        detail_label = ctk.CTkLabel(
            row_frame,
            text=detail_text,
            font=SMALL_FONT,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        detail_label.grid(row=1, column=1, sticky="w")

        # 状态
        status_text, status_color = self._format_status(plugin.status)
        self._status_line_label = ctk.CTkLabel(
            row_frame,
            text=L.t("manage.status.label", status=status_text),
            font=SMALL_FONT,
            text_color=status_color,
            anchor="w",
        )
        self._status_line_label.grid(row=2, column=1, sticky="w", pady=(0, PADDING_STANDARD))

        # 操作按钮
        btn_column = 2
        btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=btn_column, rowspan=3, padx=(0, PADDING_LARGE), pady=PADDING_STANDARD, sticky="e")

        if plugin.status == "missing_folder":
            cleanup_btn = ctk.CTkButton(
                btn_frame,
                text=L.t("manage.btn.remove_entry"),
                font=SMALL_FONT,
                fg_color=WARNING_ORANGE,
                hover_color="#f57c00",
                width=100,
                height=30,
                command=lambda p=plugin: self._on_remove_entry(p),
            )
            cleanup_btn.pack(side="right", padx=(PADDING_SMALL, 0))
        elif plugin.status == "unregistered":
            register_btn = ctk.CTkButton(
                btn_frame,
                text=L.t("manage.btn.register"),
                font=SMALL_FONT,
                fg_color=ACCENT_BLUE,
                hover_color=ACCENT_BLUE_HOVER,
                width=80,
                height=30,
                command=lambda p=plugin: self._on_register(p),
            )
            register_btn.pack(side="right", padx=(PADDING_SMALL, 0))

            uninstall_btn = ctk.CTkButton(
                btn_frame,
                text=L.t("manage.btn.uninstall"),
                font=SMALL_FONT,
                fg_color=DANGER_RED,
                hover_color=DANGER_RED_HOVER,
                width=80,
                height=30,
                command=lambda p=plugin: self._on_uninstall_clicked(p),
            )
            uninstall_btn.pack(side="right")
        else:
            uninstall_btn = ctk.CTkButton(
                btn_frame,
                text=L.t("manage.btn.uninstall"),
                font=SMALL_FONT,
                fg_color=DANGER_RED,
                hover_color=DANGER_RED_HOVER,
                width=90,
                height=30,
                command=lambda p=plugin: self._on_uninstall_clicked(p),
            )
            uninstall_btn.pack(side="right")

        return row_frame

    @staticmethod
    def _format_status(status: str) -> tuple[str, str]:
        """状态映射 (显示文字, 颜色)。"""
        status_map = {
            "enabled": (L.t("manage.status.enabled"), SUCCESS_GREEN),
            "disabled": (L.t("manage.status.disabled"), TEXT_MUTED),
            "unregistered": (L.t("manage.status.unregistered"), WARNING_ORANGE),
            "missing_folder": (L.t("manage.status.missing"), ERROR_RED),
        }
        return status_map.get(status, (status, TEXT_PRIMARY))

    # ── 操作 ──────────────────────────────────────────────────────

    def _on_uninstall_clicked(self, plugin: InstalledPlugin) -> None:
        if not show_confirm_dialog(
            self.winfo_toplevel(),
            L.t("dialog.uninstall.title"),
            L.t("dialog.uninstall.msg",
                name=plugin.name,
                version=plugin.version,
                plugin_id=plugin.plugin_id),
        ):
            return

        self._status_label.configure(text=L.t("manage.status.uninstalling"))

        def run() -> None:
            try:
                uninstall_plugin(plugin.plugin_id, plugin.version)
                self.after(0, self._on_uninstall_success, plugin.name)
            except UninstallError as e:
                self.after(0, self._on_uninstall_error, str(e))
            except Exception as e:
                self.after(0, self._on_uninstall_error, f"{L.t('gen.unexpected_error')}: {e}")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def _on_uninstall_success(self, plugin_name: str) -> None:
        self._status_label.configure(text=L.t("manage.uninstall_success", name=plugin_name))
        show_success_dialog(
            self.winfo_toplevel(),
            L.t("dialog.uninstall_success.title"),
            L.t("dialog.uninstall_success.msg", name=plugin_name),
        )
        self.refresh()

    def _on_uninstall_error(self, error_msg: str) -> None:
        self._status_label.configure(text=L.t("manage.status.uninstall_failed"))
        show_error_dialog(
            self.winfo_toplevel(),
            L.t("dialog.uninstall_failed.title"),
            error_msg,
        )
        self.refresh()

    def _on_register(self, plugin: InstalledPlugin) -> None:
        from ..core.psjson import read_psjson, write_psjson_with_retry
        from ..constants import build_psjson_entry

        try:
            data = read_psjson()
            new_entry = build_psjson_entry(
                plugin_id=plugin.plugin_id,
                name=plugin.name,
                version=plugin.version,
            )
            data["plugins"] = [
                p for p in data["plugins"] if p.get("pluginId") != plugin.plugin_id
            ]
            data["plugins"].append(new_entry)
            write_psjson_with_retry(data)

            self._status_label.configure(
                text=L.t("manage.register_success", name=plugin.name)
            )
            show_success_dialog(
                self.winfo_toplevel(),
                L.t("dialog.register_success.title"),
                L.t("dialog.register_success.msg", name=plugin.name),
            )
        except Exception as e:
            show_error_dialog(
                self.winfo_toplevel(),
                L.t("dialog.register_failed.title"),
                str(e),
            )
        finally:
            self.refresh()

    def _on_remove_entry(self, plugin: InstalledPlugin) -> None:
        if not show_confirm_dialog(
            self.winfo_toplevel(),
            L.t("dialog.remove_entry.title"),
            L.t("dialog.remove_entry.msg",
                name=plugin.name,
                plugin_id=plugin.plugin_id),
        ):
            return

        from ..core.psjson import read_psjson, write_psjson_with_retry, remove_plugin_entry, PluginNotFoundError

        try:
            data = read_psjson()
            data = remove_plugin_entry(data, plugin.plugin_id)
            write_psjson_with_retry(data)
            self._status_label.configure(
                text=L.t("manage.remove_entry_success", name=plugin.name)
            )
        except PluginNotFoundError:
            self._status_label.configure(text=L.t("manage.entry_already_removed"))
        except Exception as e:
            show_error_dialog(
                self.winfo_toplevel(),
                L.t("dialog.register_failed.title"),
                str(e),
            )
        finally:
            self.refresh()
