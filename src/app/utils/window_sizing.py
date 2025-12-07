"""
Helpers for calculating window dimensions and modal sizing consistently.
"""
from __future__ import annotations

from dataclasses import dataclass

import tkinter as tk

from ui.theme_tokens import AppConfig


@dataclass(frozen=True)
class WindowSize:
    """Represents default and minimum sizing for a window."""

    width: int
    height: int
    min_width: int
    min_height: int


_APP_WINDOW = WindowSize(
    width=AppConfig.WINDOW_WIDTH,
    height=AppConfig.WINDOW_HEIGHT,
    min_width=AppConfig.MIN_WINDOW_WIDTH,
    min_height=AppConfig.MIN_WINDOW_HEIGHT,
)

_LOGIN_MODAL = WindowSize(width=int(520 * 0.85 * 0.85), height=420, min_width=int(520 * 0.85 * 0.85), min_height=420)
_CHATROOM_MODAL = WindowSize(width=530, height=450, min_width=530, min_height=450)
_CHAT_WINDOW = WindowSize(width=500, height=575, min_width=500, min_height=575)
_MANUAL_PAIR_MODAL = WindowSize(width=500, height=475, min_width=500, min_height=475)


def get_app_window_size() -> WindowSize:
    return _APP_WINDOW


def get_login_modal_size() -> WindowSize:
    return _LOGIN_MODAL


def get_chatroom_modal_size() -> WindowSize:
    return _CHATROOM_MODAL


def get_chat_window_size() -> WindowSize:
    return _CHAT_WINDOW


def get_manual_pair_modal_size() -> WindowSize:
    return _MANUAL_PAIR_MODAL


def calculate_initial_window_size(root: tk.Misc) -> tuple[int, int]:
    """Calculate the initial dimensions based on screen size and configured ratios."""
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    width_ratio = AppConfig.WINDOW_WIDTH_RATIO * 0.94
    app_size = get_app_window_size()
    target_w = min(app_size.width, int(screen_w * width_ratio))
    target_h = min(app_size.height, int(screen_h * AppConfig.WINDOW_HEIGHT_RATIO))
    target_w = max(target_w, min(app_size.min_width, screen_w))
    target_h = max(target_h, min(app_size.min_height, screen_h))
    return target_w, target_h


def calculate_minimum_window_size(width: int, height: int, *, height_ratio: float = 0.9) -> tuple[int, int]:
    """Determine the minimum allowed size based on initial dimensions."""
    min_height = max(int(height * height_ratio), AppConfig.MIN_WINDOW_HEIGHT)
    return width, min_height


def scale_dimensions(width: int, height: int, width_scale: float, height_scale: float) -> tuple[int, int]:
    """Scale width/height by the provided ratios."""
    target_w = int(width * width_scale)
    target_h = int(height * height_scale)
    return target_w, target_h
