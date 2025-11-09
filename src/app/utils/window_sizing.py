"""
Helpers for calculating window dimensions and modal sizing consistently.
"""
from __future__ import annotations

import tkinter as tk

from utils.design_system import AppConfig


def calculate_initial_window_size(root: tk.Misc) -> tuple[int, int]:
    """Calculate the initial dimensions based on screen size and configured ratios."""
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    target_w = int(screen_w * AppConfig.WINDOW_WIDTH_RATIO)
    target_h = int(screen_h * AppConfig.WINDOW_HEIGHT_RATIO)
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
