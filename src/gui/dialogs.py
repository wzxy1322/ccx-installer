"""
模态对话框 — 确认、错误、成功、警告。
使用 L.t() 获取按钮文字，自动跟随当前语言。
"""

import customtkinter as ctk

from ..locale import L
from .styles import (
    ACCENT_BLUE,
    ACCENT_BLUE_HOVER,
    BODY_FONT,
    ERROR_RED,
    PADDING_LARGE,
    PADDING_STANDARD,
    TEXT_PRIMARY,
    WARNING_ORANGE,
)


def show_confirm_dialog(parent: ctk.CTk, title: str, message: str) -> bool:
    """显示确认对话框（是/否）。"""
    result: list[bool] = []

    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("420x180")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    _center_on_parent(dialog, parent)

    label = ctk.CTkLabel(
        dialog,
        text=message,
        font=BODY_FONT,
        wraplength=380,
        justify="left",
    )
    label.pack(pady=(PADDING_LARGE, PADDING_STANDARD), padx=PADDING_LARGE)

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=(0, PADDING_LARGE))

    def on_yes() -> None:
        result.append(True)
        dialog.destroy()

    def on_no() -> None:
        result.append(False)
        dialog.destroy()

    ctk.CTkButton(
        btn_frame,
        text=L.t("btn.yes"),
        fg_color=ACCENT_BLUE,
        hover_color=ACCENT_BLUE_HOVER,
        width=100,
        command=on_yes,
    ).pack(side="left", padx=(0, PADDING_STANDARD))

    ctk.CTkButton(
        btn_frame,
        text=L.t("btn.no"),
        fg_color="transparent",
        border_width=1,
        border_color=ACCENT_BLUE,
        hover_color=ACCENT_BLUE_HOVER,
        width=100,
        command=on_no,
    ).pack(side="right")

    dialog.wait_window()
    return result[0] if result else False


def show_error_dialog(parent: ctk.CTk, title: str, message: str) -> None:
    """显示错误对话框。"""
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("450x200")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    header_frame = ctk.CTkFrame(dialog, fg_color=ERROR_RED, height=4)
    header_frame.pack(fill="x")

    content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=PADDING_LARGE)

    error_label = ctk.CTkLabel(
        content_frame,
        text="✗",
        font=("Segoe UI", 28, "bold"),
        text_color=ERROR_RED,
    )
    error_label.pack(side="left", padx=(0, PADDING_LARGE))

    msg_label = ctk.CTkLabel(
        content_frame,
        text=message,
        font=BODY_FONT,
        wraplength=320,
        justify="left",
    )
    msg_label.pack(side="left", fill="both", expand=True)

    ctk.CTkButton(
        dialog,
        text=L.t("btn.ok"),
        fg_color=ACCENT_BLUE,
        hover_color=ACCENT_BLUE_HOVER,
        width=100,
        command=dialog.destroy,
    ).pack(pady=(0, PADDING_LARGE))

    _center_on_parent(dialog, parent)
    dialog.focus_force()
    dialog.wait_window()


def show_success_dialog(parent: ctk.CTk, title: str, message: str) -> None:
    """显示成功对话框（5 秒后自动关闭）。"""
    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("420x180")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    header_frame = ctk.CTkFrame(dialog, fg_color=ACCENT_BLUE, height=4)
    header_frame.pack(fill="x")

    content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=PADDING_LARGE)

    check_label = ctk.CTkLabel(
        content_frame,
        text="✓",
        font=("Segoe UI", 28, "bold"),
        text_color=ACCENT_BLUE,
    )
    check_label.pack(side="left", padx=(0, PADDING_LARGE))

    msg_label = ctk.CTkLabel(
        content_frame,
        text=message,
        font=BODY_FONT,
        wraplength=280,
        justify="left",
    )
    msg_label.pack(side="left", fill="both", expand=True)

    ctk.CTkButton(
        dialog,
        text=L.t("btn.ok"),
        fg_color=ACCENT_BLUE,
        hover_color=ACCENT_BLUE_HOVER,
        width=100,
        command=dialog.destroy,
    ).pack(pady=(0, PADDING_LARGE))

    _center_on_parent(dialog, parent)
    dialog.focus_force()

    dialog.after(5000, dialog.destroy)
    dialog.wait_window()


def show_warning_dialog(parent: ctk.CTk, title: str, message: str) -> bool:
    """显示警告对话框（继续/取消）。"""
    result: list[bool] = []

    dialog = ctk.CTkToplevel(parent)
    dialog.title(title)
    dialog.geometry("450x200")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()

    header_frame = ctk.CTkFrame(dialog, fg_color=WARNING_ORANGE, height=4)
    header_frame.pack(fill="x")

    content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    content_frame.pack(fill="both", expand=True, padx=PADDING_LARGE, pady=PADDING_LARGE)

    warn_label = ctk.CTkLabel(
        content_frame,
        text="⚠",
        font=("Segoe UI", 28, "bold"),
        text_color=WARNING_ORANGE,
    )
    warn_label.pack(side="left", padx=(0, PADDING_LARGE))

    msg_label = ctk.CTkLabel(
        content_frame,
        text=message,
        font=BODY_FONT,
        wraplength=310,
        justify="left",
    )
    msg_label.pack(side="left", fill="both", expand=True)

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(pady=(0, PADDING_LARGE))

    def on_continue() -> None:
        result.append(True)
        dialog.destroy()

    def on_cancel() -> None:
        result.append(False)
        dialog.destroy()

    ctk.CTkButton(
        btn_frame,
        text=L.t("btn.continue"),
        fg_color=WARNING_ORANGE,
        hover_color="#f57c00",
        width=110,
        command=on_continue,
    ).pack(side="left", padx=(0, PADDING_STANDARD))

    ctk.CTkButton(
        btn_frame,
        text=L.t("btn.cancel"),
        fg_color="transparent",
        border_width=1,
        border_color=TEXT_PRIMARY,
        width=100,
        command=on_cancel,
    ).pack(side="right")

    _center_on_parent(dialog, parent)
    dialog.focus_force()
    dialog.wait_window()
    return result[0] if result else False


def _center_on_parent(dialog: ctk.CTkToplevel, parent: ctk.CTk) -> None:
    """将对话框居中于父窗口。"""
    dialog.update_idletasks()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    px, py = parent.winfo_x(), parent.winfo_y()
    dw, dh = dialog.winfo_width(), dialog.winfo_height()
    x = px + (pw - dw) // 2
    y = py + (ph - dh) // 2
    dialog.geometry(f"+{x}+{y}")
