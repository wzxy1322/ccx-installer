"""
安装标签页 — 浏览/拖拽 .ccx 文件，查看插件信息，一键安装。
支持 L.toggle() 中英文切换。
"""

import os
import queue
import threading
import time
from typing import Callable

import customtkinter as ctk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES

from ..core.ccx_parser import CcxInfo, CcxParseError, parse_ccx
from ..core.installer import InstallError, install_plugin
from ..core.scanner import scan_installed_plugins
from ..locale import L
from .dialogs import show_confirm_dialog, show_error_dialog, show_success_dialog, show_warning_dialog
from .styles import (
    ACCENT_BLUE,
    ACCENT_BLUE_HOVER,
    BG_ENTRY,
    BG_FRAME,
    BODY_FONT,
    BUTTON_HEIGHT,
    BUTTON_WIDTH_LARGE,
    BUTTON_WIDTH_STANDARD,
    ERROR_RED,
    MONO_FONT,
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

DROPZONE_IDLE_COLOR = "#555555"
DROPZONE_HOVER_COLOR = ACCENT_BLUE
DROPZONE_IDLE_BG = BG_FRAME
DROPZONE_HOVER_BG = "#1a3a5c"


class InstallTab(ctk.CTkFrame):
    """「安装插件」标签页。"""

    def __init__(self, master, on_plugin_installed: Callable[[], None]):
        super().__init__(master)
        self._on_plugin_installed = on_plugin_installed
        self._ccx_path: str | None = None
        self._ccx_info: CcxInfo | None = None
        self._is_installing = False
        self._progress_queue: queue.Queue[str] = queue.Queue()

        self._build_ui()

    # ── UI 构建 ────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        # ── 浏览选择区 ──
        self._browse_frame = ctk.CTkFrame(self)
        self._browse_frame.grid(row=0, column=0, sticky="ew", padx=PADDING_XL, pady=(PADDING_XL, PADDING_STANDARD))
        self._browse_frame.grid_columnconfigure(1, weight=1)

        self._select_label = ctk.CTkLabel(
            self._browse_frame,
            text=L.t("install.select.label"),
            font=SUBHEADING_FONT,
            text_color=TEXT_PRIMARY,
        )
        self._select_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=PADDING_LARGE, pady=(PADDING_STANDARD, PADDING_SMALL))

        self._path_entry = ctk.CTkEntry(
            self._browse_frame,
            font=SMALL_FONT,
            placeholder_text=L.t("install.path.placeholder"),
            state="readonly",
        )
        self._path_entry.grid(row=1, column=0, sticky="ew", padx=(PADDING_LARGE, PADDING_SMALL), pady=(0, PADDING_STANDARD))

        self._browse_btn = ctk.CTkButton(
            self._browse_frame,
            text=L.t("install.browse.btn"),
            font=BODY_FONT,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            width=BUTTON_WIDTH_STANDARD,
            height=BUTTON_HEIGHT,
            command=self._on_browse_clicked,
        )
        self._browse_btn.grid(row=1, column=1, sticky="e", padx=(0, PADDING_LARGE), pady=(0, PADDING_STANDARD))

        # ── 拖拽区 ──
        self._drop_zone = ctk.CTkFrame(
            self,
            height=100,
            border_width=2,
            border_color=DROPZONE_IDLE_COLOR,
            fg_color=DROPZONE_IDLE_BG,
        )
        self._drop_zone.grid(row=1, column=0, sticky="ew", padx=PADDING_XL, pady=(0, PADDING_STANDARD))
        self._drop_zone.grid_columnconfigure(0, weight=1)
        self._drop_zone.grid_rowconfigure(0, weight=1)
        self._drop_zone.grid_propagate(False)

        self._drop_label = ctk.CTkLabel(
            self._drop_zone,
            text=L.t("install.drop.label"),
            font=BODY_FONT,
            text_color=TEXT_MUTED,
            justify="center",
        )
        self._drop_label.grid(row=0, column=0, sticky="nsew")

        self._drop_zone.drop_target_register(DND_FILES)
        self._drop_zone.dnd_bind("<<Drop>>", self._on_drop)
        self._drop_zone.dnd_bind("<<DragEnter>>", self._on_drag_enter)
        self._drop_zone.dnd_bind("<<DragLeave>>", self._on_drag_leave)

        # ── 插件信息区 ──
        self._info_frame = ctk.CTkFrame(self)
        self._info_frame.grid(row=2, column=0, sticky="ew", padx=PADDING_XL, pady=PADDING_STANDARD)
        self._info_frame.grid_columnconfigure(0, weight=1)

        self._info_heading = ctk.CTkLabel(
            self._info_frame,
            text=L.t("install.info.heading"),
            font=SUBHEADING_FONT,
            text_color=TEXT_PRIMARY,
        )
        self._info_heading.grid(row=0, column=0, sticky="w", padx=PADDING_LARGE, pady=(PADDING_STANDARD, PADDING_SMALL))

        self._info_content = ctk.CTkFrame(self._info_frame, fg_color="transparent")
        self._info_content.grid(row=1, column=0, sticky="ew", padx=PADDING_LARGE, pady=(0, PADDING_STANDARD))
        self._info_content.grid_columnconfigure(1, weight=1)

        self._icon_label = ctk.CTkLabel(
            self._info_content,
            text="📦",
            font=("Segoe UI", 36),
        )
        self._icon_label.grid(row=0, column=0, rowspan=6, padx=(0, PADDING_LARGE), sticky="n")

        # 信息行 — 存储 key 和 label widget 的引用
        self._info_field_keys = ["name", "id", "version", "host", "panels"]
        self._info_field_labels: dict[str, ctk.CTkLabel] = {}  # 字段名标签
        self._info_values: dict[str, ctk.CTkLabel] = {}         # 字段值标签

        for i, key in enumerate(self._info_field_keys):
            field_label = ctk.CTkLabel(
                self._info_content,
                text="",
                font=SMALL_FONT,
                text_color=TEXT_MUTED,
                anchor="w",
            )
            field_label.grid(row=i, column=1, sticky="w", pady=(0, 0))
            self._info_field_labels[key] = field_label

            value_label = ctk.CTkLabel(
                self._info_content,
                text=L.t("install.info.na"),
                font=BODY_FONT,
                text_color=TEXT_PRIMARY,
                anchor="w",
            )
            value_label.grid(row=i, column=2, sticky="w", padx=(PADDING_SMALL, 0))
            self._info_values[key] = value_label

        self._refresh_info_field_labels()
        self._hide_info_card()

        # ── 安装按钮 ──
        self._install_btn = ctk.CTkButton(
            self,
            text=L.t("install.btn.default"),
            font=SUBHEADING_FONT,
            fg_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            width=BUTTON_WIDTH_LARGE,
            height=48,
            state="disabled",
            command=self._on_install_clicked,
        )
        self._install_btn.grid(row=3, column=0, pady=PADDING_STANDARD)

        # ── 状态区 ──
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=4, column=0, sticky="nsew", padx=PADDING_XL, pady=(PADDING_STANDARD, PADDING_XL))
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_rowconfigure(2, weight=1)

        self._status_label = ctk.CTkLabel(
            status_frame,
            text=L.t("install.status.label"),
            font=SUBHEADING_FONT,
            text_color=TEXT_PRIMARY,
        )
        self._status_label.grid(row=0, column=0, sticky="w", padx=PADDING_LARGE, pady=(PADDING_STANDARD, PADDING_SMALL))

        self._status_box = ctk.CTkTextbox(
            status_frame,
            font=MONO_FONT,
            fg_color=BG_ENTRY,
            wrap="word",
            height=120,
            state="disabled",
        )
        self._status_box.grid(row=1, column=0, sticky="ew", padx=PADDING_LARGE, pady=(0, PADDING_STANDARD))

        self._status_box.tag_config("info", foreground=TEXT_PRIMARY)
        self._status_box.tag_config("success", foreground=SUCCESS_GREEN)
        self._status_box.tag_config("error", foreground=ERROR_RED)
        self._status_box.tag_config("warning", foreground=WARNING_ORANGE)

        self.grid_rowconfigure(4, weight=1)

    # ── 语言刷新 ──────────────────────────────────────────────────

    def _refresh_language(self) -> None:
        """语言切换时刷新所有静态文本。"""
        self._select_label.configure(text=L.t("install.select.label"))
        self._path_entry.configure(placeholder_text=L.t("install.path.placeholder"))
        self._browse_btn.configure(text=L.t("install.browse.btn"))
        self._drop_label.configure(text=L.t("install.drop.label"))
        self._info_heading.configure(text=L.t("install.info.heading"))
        self._status_label.configure(text=L.t("install.status.label"))

        # 刷新字段标签
        self._refresh_info_field_labels()
        # 刷新安装按钮（保持当前状态）
        if self._is_installing:
            self._install_btn.configure(text=L.t("install.btn.installing"))
        elif not self._ccx_info:
            self._install_btn.configure(text=L.t("install.btn.default"))
        # 否则保持当前 install/reinstall/update 状态不变
        # （这些由 _load_ccx 或 _install_complete 设置）

    def _refresh_info_field_labels(self) -> None:
        """刷新信息字段名标签的文字。"""
        field_key_map = {
            "name": "install.info.field.name",
            "id": "install.info.field.id",
            "version": "install.info.field.version",
            "host": "install.info.field.host",
            "panels": "install.info.field.panels",
        }
        for key, locale_key in field_key_map.items():
            if key in self._info_field_labels:
                self._info_field_labels[key].configure(text=f"{L.t(locale_key)}:")

    # ── 拖拽处理 ──────────────────────────────────────────────────

    def _on_drop(self, event) -> None:
        self._set_drop_zone_idle()

        raw_data = event.data.strip()
        if raw_data.startswith("{") and raw_data.endswith("}"):
            raw_data = raw_data[1:-1]

        paths = raw_data.split("} {") if "} {" in raw_data else [raw_data]
        paths = [p.strip("{}") for p in paths]

        ccx_path = None
        for p in paths:
            if p.lower().endswith(".ccx"):
                ccx_path = p
                break

        if not ccx_path:
            self._append_status(L.t("install.status.drop_ccx"), "warning")
            return

        if not os.path.isfile(ccx_path):
            self._append_status(L.t("install.status.file_not_found", path=ccx_path), "error")
            return

        self._load_ccx(ccx_path)

    def _on_drag_enter(self, event) -> None:
        self._drop_zone.configure(
            border_color=DROPZONE_HOVER_COLOR,
            fg_color=DROPZONE_HOVER_BG,
        )
        self._drop_label.configure(text_color=TEXT_PRIMARY)

    def _on_drag_leave(self, event) -> None:
        self._set_drop_zone_idle()

    def _set_drop_zone_idle(self) -> None:
        self._drop_zone.configure(
            border_color=DROPZONE_IDLE_COLOR,
            fg_color=DROPZONE_IDLE_BG,
        )
        self._drop_label.configure(text_color=TEXT_MUTED)

    # ── 操作 ──────────────────────────────────────────────────────

    def _on_browse_clicked(self) -> None:
        path = filedialog.askopenfilename(
            title=L.t("install.dialog.title"),
            filetypes=[(L.t("install.dialog.filetype"), "*.ccx"), ("All Files", "*.*")],
        )
        if not path:
            return
        self._load_ccx(path)

    def _load_ccx(self, path: str) -> None:
        self._ccx_path = path
        self._path_entry.configure(state="normal")
        self._path_entry.delete(0, "end")
        self._path_entry.insert(0, path)
        self._path_entry.configure(state="readonly")

        self._append_status(L.t("install.status.loading", filename=os.path.basename(path)), "info")

        try:
            self._ccx_info = parse_ccx(path)
        except CcxParseError as e:
            self._append_status(f"Error: {e}", "error")
            show_error_dialog(self.winfo_toplevel(), L.t("dialog.invalid_ccx"), str(e))
            self._hide_info_card()
            self._install_btn.configure(state="disabled")
            self._show_drop_zone()
            return

        self._populate_plugin_info(self._ccx_info)
        self._append_status(L.t("install.status.valid"), "success")

        installed = scan_installed_plugins()
        existing = next((p for p in installed if p.plugin_id == self._ccx_info.plugin_id), None)
        if existing:
            if existing.version == self._ccx_info.version:
                self._install_btn.configure(text=L.t("install.btn.reinstall"))
                self._append_status(
                    L.t("install.status.note_installed", version=existing.version), "warning"
                )
            else:
                self._install_btn.configure(text=L.t(
                    "install.btn.update", old=existing.version, new=self._ccx_info.version
                ))
                self._append_status(
                    L.t("install.status.found_old", old=existing.version), "warning"
                )
        else:
            self._install_btn.configure(text=L.t("install.btn.default"))

        self._install_btn.configure(state="normal")
        self._hide_drop_zone()

    def _show_drop_zone(self) -> None:
        self._drop_zone.grid(row=1, column=0, sticky="ew", padx=PADDING_XL, pady=(0, PADDING_STANDARD))

    def _hide_drop_zone(self) -> None:
        self._drop_zone.grid_remove()

    def _populate_plugin_info(self, info: CcxInfo) -> None:
        self._info_heading.grid()
        self._info_content.grid()

        self._info_values["name"].configure(text=info.name)
        self._info_values["id"].configure(text=info.plugin_id)
        self._info_values["version"].configure(text=f"v{info.version}")

        host_text = info.host_app
        if info.host_min_version:
            host_text += f" ≥ {info.host_min_version}"
        self._info_values["host"].configure(text=host_text)

        panels_text = ", ".join(info.panel_labels) if info.panel_labels else L.t("install.info.na")
        self._info_values["panels"].configure(text=panels_text)

    def _hide_info_card(self) -> None:
        self._info_heading.grid_remove()
        self._info_content.grid_remove()

    def _on_install_clicked(self) -> None:
        if self._is_installing:
            return

        if not self._ccx_path or not self._ccx_info:
            show_error_dialog(
                self.winfo_toplevel(),
                L.t("dialog.no_plugin.title"),
                L.t("dialog.no_plugin.msg"),
            )
            return

        if self._ccx_info.host_app != "PS" and self._ccx_info.host_app != "unknown":
            if not show_warning_dialog(
                self.winfo_toplevel(),
                L.t("dialog.non_ps.title"),
                L.t("dialog.non_ps.msg", app=self._ccx_info.host_app),
            ):
                return

        installed = scan_installed_plugins()
        existing = next((p for p in installed if p.plugin_id == self._ccx_info.plugin_id), None)
        if existing:
            if existing.version == self._ccx_info.version:
                if not show_confirm_dialog(
                    self.winfo_toplevel(),
                    L.t("dialog.reinstall.title"),
                    L.t("dialog.reinstall.msg", version=existing.version),
                ):
                    return
            else:
                if not show_confirm_dialog(
                    self.winfo_toplevel(),
                    L.t("dialog.update.title"),
                    L.t("dialog.update.msg", old=existing.version, new=self._ccx_info.version),
                ):
                    return

        self._start_install()

    def _start_install(self) -> None:
        self._is_installing = True
        self._install_btn.configure(state="disabled", text=L.t("install.btn.installing"))
        self._progress_queue = queue.Queue()

        def progress_cb(msg: str) -> None:
            self._progress_queue.put(msg)

        def run() -> None:
            try:
                install_plugin(
                    self._ccx_path,  # type: ignore[arg-type]
                    self._ccx_info,  # type: ignore[arg-type]
                    progress_callback=progress_cb,
                )
                self._progress_queue.put("__SUCCESS__")
            except InstallError as e:
                self._progress_queue.put(f"__ERROR__:{e}")
            except Exception as e:
                self._progress_queue.put(f"__ERROR__:{L.t('gen.unexpected_error')}: {e}")

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self._poll_progress()

    def _poll_progress(self) -> None:
        try:
            while True:
                msg = self._progress_queue.get_nowait()
                if msg == "__SUCCESS__":
                    self._install_complete(success=True)
                    return
                elif msg.startswith("__ERROR__:"):
                    error_msg = msg[len("__ERROR__:"):]
                    self._install_complete(success=False, error=error_msg)
                    return
                else:
                    self._append_status(msg, "info")
        except queue.Empty:
            pass

        if self._is_installing:
            self.after(100, self._poll_progress)

    def _install_complete(self, success: bool, error: str | None = None) -> None:
        self._is_installing = False

        if success:
            version = self._ccx_info.version if self._ccx_info else ""
            name = self._ccx_info.name if self._ccx_info else L.t("gen.plugin_fallback")
            self._append_status(
                L.t("install.success_status", name=name, version=version), "success"
            )
            self._append_status(L.t("install.restart_warning"), "warning")
            self._install_btn.configure(state="disabled", text=L.t("install.btn.installed"))
            show_success_dialog(
                self.winfo_toplevel(),
                L.t("dialog.install_success.title"),
                L.t("dialog.install_success.msg", name=name, version=version),
            )
            self._on_plugin_installed()
        else:
            self._append_status(
                L.t("install.failed_status", error=error), "error"
            )
            self._install_btn.configure(state="normal", text=L.t("install.btn.default"))
            show_error_dialog(
                self.winfo_toplevel(),
                L.t("dialog.install_failed.title"),
                error or L.t("gen.unexpected_error"),
            )

    def _append_status(self, message: str, tag: str = "info") -> None:
        self._status_box.configure(state="normal")
        timestamp = time.strftime("%H:%M:%S")
        self._status_box.insert("end", f"[{timestamp}] ", ("info",))
        self._status_box.insert("end", f"{message}\n", (tag,))
        self._status_box.see("end")
        self._status_box.configure(state="disabled")
