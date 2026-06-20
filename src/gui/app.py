"""
主窗口 — 标签页容器、状态栏、语言切换。
"""

import customtkinter as ctk

from ..constants import WINDOW_HEIGHT, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_WIDTH
from ..locale import L
from .install_tab import InstallTab
from .manage_tab import ManageTab
from .styles import (
    ACCENT_BLUE,
    ACCENT_BLUE_HOVER,
    BG_DARK,
    PADDING_LARGE,
    PADDING_SMALL,
    SMALL_FONT,
    TEXT_MUTED,
    TEXT_PRIMARY,
)


class CcxInstallerApp(ctk.CTk):
    """CCX 插件安装器主窗口。"""

    def __init__(self):
        super().__init__()

        self.title(L.t("app.title"))
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - WINDOW_WIDTH) // 2
        y = (sh - WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_tabs()
        self._build_status_bar()

        self._install_tab: InstallTab = None  # type: ignore[assignment]
        self._manage_tab: ManageTab = None  # type: ignore[assignment]

        self._create_tabs()

        # 注册语言切换回调
        L.on_switch(self._refresh_language)

    # ── UI 构建 ────────────────────────────────────────────────────

    def _build_header(self) -> None:
        """构建标题栏 + 语言切换按钮。"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=PADDING_LARGE, pady=(PADDING_LARGE, 0))
        header.grid_columnconfigure(0, weight=1)

        self._title_label = ctk.CTkLabel(
            header,
            text=L.t("app.title"),
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT_PRIMARY,
        )
        self._title_label.grid(row=0, column=0, sticky="w")

        self._subtitle_label = ctk.CTkLabel(
            header,
            text=L.t("app.subtitle"),
            font=SMALL_FONT,
            text_color=TEXT_MUTED,
        )
        self._subtitle_label.grid(row=1, column=0, sticky="w")

        # 语言切换按钮
        self._lang_btn = ctk.CTkButton(
            header,
            text=L.t("app.lang.btn"),
            font=("Segoe UI", 12, "bold"),
            fg_color="transparent",
            border_width=1,
            border_color=ACCENT_BLUE,
            hover_color=ACCENT_BLUE_HOVER,
            width=40,
            height=30,
            command=L.toggle,
        )
        self._lang_btn.grid(row=0, column=1, rowspan=2, sticky="e", padx=(PADDING_LARGE, 0))

    def _build_tabs(self) -> None:
        """构建标签页容器。"""
        self._tabview = ctk.CTkTabview(self)
        self._tabview.grid(row=1, column=0, sticky="nsew", padx=PADDING_LARGE, pady=PADDING_LARGE)

        self._tabview.configure(
            fg_color=BG_DARK,
            text_color=TEXT_PRIMARY,
            text_color_disabled=TEXT_MUTED,
        )

        self._tabview.add(L.t("app.tab.install"))
        self._tabview.add(L.t("app.tab.manage"))

    def _create_tabs(self) -> None:
        """创建标签页内容。"""
        self._install_tab = InstallTab(
            self._tabview.tab(L.t("app.tab.install")),
            on_plugin_installed=self._on_plugin_installed,
        )
        self._install_tab.pack(fill="both", expand=True)

        self._manage_tab = ManageTab(self._tabview.tab(L.t("app.tab.manage")))
        self._manage_tab.pack(fill="both", expand=True)

        self._manage_tab.refresh()

    def _build_status_bar(self) -> None:
        """构建底部状态栏。"""
        self._status_bar = ctk.CTkLabel(
            self,
            text=L.t("app.status.ready"),
            font=SMALL_FONT,
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self._status_bar.grid(row=2, column=0, sticky="ew", padx=PADDING_LARGE, pady=(0, PADDING_SMALL))

    # ── 语言刷新 ──────────────────────────────────────────────────

    def _refresh_language(self) -> None:
        """语言切换时更新主窗口和子组件文本。"""
        self.title(L.t("app.title"))
        self._title_label.configure(text=L.t("app.title"))
        self._subtitle_label.configure(text=L.t("app.subtitle"))
        self._lang_btn.configure(text=L.t("app.lang.btn"))
        self._status_bar.configure(text=L.t("app.status.ready"))

        # 重命名标签页 (CTkTabview 没有直接 API，需重建)
        # 采用销毁-重建策略
        self._install_tab._refresh_language()  # type: ignore[union-attr]
        self._manage_tab._refresh_language()  # type: ignore[union-attr]

        # 重建 tabview 标签
        self._rebuild_tab_labels()

    def _rebuild_tab_labels(self) -> None:
        """重建标签页按钮文字。"""
        try:
            # CTkTabview 内部使用 CTkSegmentedButton
            segmented = self._tabview._segmented_button
            if segmented is not None:
                btn_count = len(segmented._buttons_dict)
                if btn_count >= 2:
                    keys = list(segmented._buttons_dict.keys())
                    # 更新第一个按钮文本
                    btn0 = segmented._buttons_dict[keys[0]]
                    btn0.configure(text=L.t("app.tab.install"))
                    # 更新第二个按钮文本
                    btn1 = segmented._buttons_dict[keys[1]]
                    btn1.configure(text=L.t("app.tab.manage"))
        except Exception:
            pass  # 内部 API 可能变化，静默降级

    # ── 回调 ──────────────────────────────────────────────────────

    def _on_plugin_installed(self) -> None:
        self._manage_tab.refresh()

    def set_status(self, message: str, is_error: bool = False) -> None:
        self._status_bar.configure(
            text=message,
            text_color="#e53935" if is_error else TEXT_MUTED,
        )
