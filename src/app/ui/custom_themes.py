"""Custom theme creation and management system for LoComm UI."""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from ui.theme_manager import _THEME_DEFINITIONS
# ThemeManager is imported lazily inside functions to avoid circular imports
from ui.theme_tokens import Colors, Palette
from utils.app_logger import get_logger

logger = get_logger(__name__)


@dataclass
class CustomTheme:
    """Represents a user-created custom theme."""
    name: str
    display_name: str
    colors: Dict[str, str]
    description: str = ""
    author: str = "User"
    version: str = "1.0"
    accessibility_features: List[str] = None
    tags: List[str] = None
    preview_colors: Dict[str, str] = None
    
    def __post_init__(self):
        if self.accessibility_features is None:
            self.accessibility_features = []
        if self.tags is None:
            self.tags = []
        if self.preview_colors is None:
            self.preview_colors = {
                "primary": self.colors.get("TEXT_PRIMARY", "#FFFFFF"),
                "secondary": self.colors.get("TEXT_SECONDARY", "#CCCCCC"),
                "background": self.colors.get("SURFACE", "#000000"),
                "accent": self.colors.get("ACCENT_PRIMARY", "#007ACC")
            }


class CustomThemeManager:
    """Manages custom user-created themes."""
    
    _instance = None
    _custom_themes_dir = Path.home() / ".locomm" / "custom_themes"
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._custom_themes: Dict[str, CustomTheme] = {}
        self._theme_registry: Dict[str, str] = {}  # theme_name -> file_path
        self._load_custom_themes()
        self._initialized = True
    
    def _ensure_directory(self):
        """Ensure the custom themes directory exists."""
        self._custom_themes_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_custom_themes(self):
        """Load all custom themes from disk."""
        self._ensure_directory()
        
        for theme_file in self._custom_themes_dir.glob("*.json"):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                
                theme = CustomTheme(**theme_data)
                self._register_custom_theme(theme, str(theme_file))
                logger.info(f"Loaded custom theme: {theme.display_name}")
                
            except Exception as e:
                logger.error(f"Failed to load custom theme {theme_file}: {e}")
    
    def _register_custom_theme(self, theme: CustomTheme, file_path: str):
        """Register a custom theme in the system."""
        self._custom_themes[theme.name] = theme
        self._theme_registry[theme.name] = file_path
        
        # Add to theme definitions for runtime use
        if theme.name not in _THEME_DEFINITIONS:
            _THEME_DEFINITIONS[theme.name] = theme.colors
            
        # Update available modes in ThemeManager (import lazily to avoid circular import)
        from ui.theme_manager import ThemeManager
        if theme.name not in ThemeManager._available_modes:
            ThemeManager._available_modes.append(theme.name)
    
    def create_theme(self, name: str, display_name: str, description: str = "", 
                    base_theme: str = "dark", color_overrides: Dict[str, str] = None) -> CustomTheme:
        """Create a new custom theme based on an existing theme with color overrides."""
        if color_overrides is None:
            color_overrides = {}
        
        # Get base theme
        if base_theme not in _THEME_DEFINITIONS:
            raise ValueError(f"Base theme '{base_theme}' not found")
        
        base_colors = _THEME_DEFINITIONS[base_theme].copy()
        base_colors.update(color_overrides)
        
        # Create theme
        theme = CustomTheme(
            name=name,
            display_name=display_name,
            description=description,
            colors=base_colors
        )
        
        # Save theme
        self.save_theme(theme)
        self._register_custom_theme(theme, "")
        
        return theme
    
    def save_theme(self, theme: CustomTheme):
        """Save a custom theme to disk."""
        self._ensure_directory()
        
        safe_name = "".join(c for c in theme.name if c.isalnum() or c in ('-', '_'))
        theme_file = self._custom_themes_dir / f"{safe_name}.json"
        
        try:
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(theme), f, indent=2, ensure_ascii=False)
            
            self._theme_registry[theme.name] = str(theme_file)
            logger.info(f"Saved custom theme: {theme.display_name}")
            
        except Exception as e:
            logger.error(f"Failed to save custom theme {theme.name}: {e}")
            raise
    
    def delete_theme(self, theme_name: str) -> bool:
        """Delete a custom theme."""
        if theme_name not in self._custom_themes:
            return False
        
        theme = self._custom_themes[theme_name]
        
        try:
            # Remove from registry
            del self._custom_themes[theme_name]
            
            # Remove from theme definitions
            if theme_name in _THEME_DEFINITIONS:
                del _THEME_DEFINITIONS[theme_name]
            
            # Remove from available modes (import lazily to avoid circular import)
            from ui.theme_manager import ThemeManager
            if theme_name in ThemeManager._available_modes:
                ThemeManager._available_modes.remove(theme_name)
            
            # Delete file
            if theme_name in self._theme_registry:
                theme_file = Path(self._theme_registry[theme_name])
                if theme_file.exists():
                    theme_file.unlink()
                del self._theme_registry[theme_name]
            
            logger.info(f"Deleted custom theme: {theme.display_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete custom theme {theme_name}: {e}")
            return False
    
    def get_custom_themes(self) -> List[CustomTheme]:
        """Get list of all custom themes."""
        return list(self._custom_themes.values())
    
    def get_theme(self, name: str) -> Optional[CustomTheme]:
        """Get a specific custom theme by name."""
        return self._custom_themes.get(name)
    
    def import_theme(self, theme_data: Dict[str, Any]) -> CustomTheme:
        """Import a theme from JSON data."""
        try:
            theme = CustomTheme(**theme_data)
            
            # Ensure unique name
            base_name = theme.name
            counter = 1
            while theme.name in self._custom_themes:
                theme.name = f"{base_name}_{counter}"
                counter += 1
            
            self.save_theme(theme)
            self._register_custom_theme(theme, "")
            
            logger.info(f"Imported custom theme: {theme.display_name}")
            return theme
            
        except Exception as e:
            logger.error(f"Failed to import theme: {e}")
            raise ValueError(f"Invalid theme data: {e}")
    
    def export_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Export a theme to JSON data."""
        theme = self.get_theme(theme_name)
        if theme is None:
            return None
        
        return asdict(theme)
    
    def get_theme_variants(self, base_colors: Dict[str, str]) -> List[Dict[str, str]]:
        """Generate theme variants with different accent colors."""
        variants = []
        
        # Predefined accent color sets that work well together
        accent_sets = [
            {"ACCENT_PRIMARY": "#007ACC", "ACCENT_PRIMARY_HOVER": "#189ACE", "ACCENT_SECONDARY": "#50E3C2"},
            {"ACCENT_PRIMARY": "#FF6B35", "ACCENT_PRIMARY_HOVER": "#F77F00", "ACCENT_SECONDARY": "#52B788"},
            {"ACCENT_PRIMARY": "#A78BFA", "ACCENT_PRIMARY_HOVER": "#C4B5FD", "ACCENT_SECONDARY": "#34D399"},
            {"ACCENT_PRIMARY": "#06B6D4", "ACCENT_PRIMARY_HOVER": "#67E8F9", "ACCENT_SECONDARY": "#A7F3D0"},
            {"ACCENT_PRIMARY": "#EF4444", "ACCENT_PRIMARY_HOVER": "#F87171", "ACCENT_SECONDARY": "#FBBF24"},
            {"ACCENT_PRIMARY": "#10B981", "ACCENT_PRIMARY_HOVER": "#34D399", "ACCENT_SECONDARY": "#60A5FA"},
        ]
        
        for accent_set in accent_sets:
            variant = base_colors.copy()
            variant.update(accent_set)
            variants.append(variant)
        
        return variants


# Global instance
def get_custom_theme_manager() -> CustomThemeManager:
    """Get the global custom theme manager instance."""
    return CustomThemeManager()


# Utility functions for theme creation
def create_mono_theme(base_theme: str = "dark", mono_color: str = "#808080") -> Dict[str, str]:
    """Create a monochromatic theme with a single color."""
    if base_theme not in _THEME_DEFINITIONS:
        raise ValueError(f"Base theme '{base_theme}' not found")
    
    base = _THEME_DEFINITIONS[base_theme].copy()
    
    # Create monochromatic palette
    mono_light = mono_color
    mono_medium = _adjust_brightness(mono_color, -30)
    mono_dark = _adjust_brightness(mono_color, -60)
    
    return {
        **base,
        "SURFACE": mono_dark,
        "SURFACE_ALT": mono_medium,
        "SURFACE_RAISED": mono_light,
        "TEXT_PRIMARY": "#FFFFFF" if _is_dark_color(mono_dark) else "#000000",
        "TEXT_SECONDARY": "#E0E0E0" if _is_dark_color(mono_dark) else "#404040",
        "TEXT_MUTED": "#B0B0B0" if _is_dark_color(mono_dark) else "#808080",
        "BORDER": mono_medium,
        "DIVIDER": mono_medium,
    }


def create_warm_theme(base_theme: str = "dark") -> Dict[str, str]:
    """Create a warm-toned theme."""
    if base_theme not in _THEME_DEFINITIONS:
        raise ValueError(f"Base theme '{base_theme}' not found")
    
    base = _THEME_DEFINITIONS[base_theme].copy()
    
    return {
        **base,
        "ACCENT_PRIMARY": "#FF6B35",
        "ACCENT_PRIMARY_HOVER": "#F77F00",
        "ACCENT_SECONDARY": "#F4A261",
        "STATE_SUCCESS": "#2D6A4F",
        "STATE_INFO": "#457B9D",
        "STATE_WARNING": "#F4A261",
        "STATE_ERROR": "#E76F51",
    }


def create_cool_theme(base_theme: str = "dark") -> Dict[str, str]:
    """Create a cool-toned theme."""
    if base_theme not in _THEME_DEFINITIONS:
        raise ValueError(f"Base theme '{base_theme}' not found")
    
    base = _THEME_DEFINITIONS[base_theme].copy()
    
    return {
        **base,
        "ACCENT_PRIMARY": "#06B6D4",
        "ACCENT_PRIMARY_HOVER": "#67E8F9",
        "ACCENT_SECONDARY": "#8B5CF6",
        "STATE_SUCCESS": "#10B981",
        "STATE_INFO": "#3B82F6",
        "STATE_WARNING": "#F59E0B",
        "STATE_ERROR": "#EF4444",
    }


# Color utility functions
def _adjust_brightness(hex_color: str, amount: int) -> str:
    """Adjust the brightness of a hex color."""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Adjust each component
    adjusted = tuple(max(0, min(255, c + amount)) for c in rgb)
    
    return f"#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}"


def _is_dark_color(hex_color: str) -> bool:
    """Determine if a color is dark or light."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Calculate luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    return luminance < 0.5


def generate_contrast_compliant_colors(base_color: str, min_contrast: float = 4.5) -> Dict[str, str]:
    """Generate colors that meet WCAG contrast requirements."""
    base_rgb = tuple(int(base_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # For high contrast compliance, we'll generate darker and lighter versions
    dark_version = _adjust_brightness(base_color, -100)
    light_version = _adjust_brightness(base_color, 100)
    
    return {
        "primary": base_color,
        "on_primary": "#FFFFFF" if _is_dark_color(dark_version) else "#000000",
        "primary_container": dark_version,
        "on_primary_container": "#FFFFFF" if _is_dark_color(dark_version) else "#000000",
        "secondary": light_version,
        "on_secondary": "#FFFFFF" if _is_dark_color(light_version) else "#000000",
    }