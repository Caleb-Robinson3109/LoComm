"""Context-aware theming system for dynamic component styling."""
from __future__ import annotations

from typing import Dict, Any, Optional, Union
from enum import Enum
import tkinter as tk

from ui.theme_tokens import Colors, Spacing
from ui.theme_manager import ThemeManager
from utils.app_logger import get_logger

logger = get_logger(__name__)


class ThemeContext(Enum):
    """Context types for different UI scenarios."""
    DEFAULT = "default"
    DIALOG = "dialog"
    MODAL = "modal"
    TOOLTIP = "tooltip"
    NOTIFICATION = "notification"
    SIDEBAR = "sidebar"
    HEADER = "header"
    FOOTER = "footer"
    CONTENT = "content"
    INPUT = "input"
    BUTTON = "button"
    CARD = "card"
    LIST_ITEM = "list_item"
    SELECTED_ITEM = "selected_item"
    HOVER_STATE = "hover_state"
    FOCUS_STATE = "focus_state"
    DISABLED_STATE = "disabled_state"
    ERROR_STATE = "error_state"
    SUCCESS_STATE = "success_state"
    WARNING_STATE = "warning_state"
    INFO_STATE = "info_state"


class ContextThemeResolver:
    """Resolves theme colors based on context and state."""
    
    _context_overrides: Dict[ThemeContext, Dict[str, str]] = {}
    _state_modifiers: Dict[str, Dict[str, float]] = {
        "hover": {"brightness": 1.1, "saturation": 1.05},
        "focus": {"brightness": 1.05, "saturation": 1.1},
        "active": {"brightness": 0.9, "saturation": 0.95},
        "disabled": {"brightness": 0.6, "saturation": 0.3},
    }
    
    @classmethod
    def register_context_override(cls, context: ThemeContext, overrides: Dict[str, str]):
        """Register context-specific color overrides."""
        cls._context_overrides[context] = overrides
        logger.debug(f"Registered context override for {context.value}")
    
    @classmethod
    def get_context_colors(cls, context: ThemeContext, base_colors: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get colors for a specific context."""
        if base_colors is None:
            base_colors = cls._get_current_theme_colors()
        
        # Start with base colors
        context_colors = base_colors.copy()
        
        # Apply context-specific overrides
        if context in cls._context_overrides:
            context_colors.update(cls._context_overrides[context])
        
        return context_colors
    
    @classmethod
    def apply_state_modifier(cls, color: str, state: str) -> str:
        """Apply state modifier (hover, focus, etc.) to a color."""
        if state not in cls._state_modifiers:
            return color
        
        modifier = cls._state_modifiers[state]
        return cls._adjust_color(color, **modifier)
    
    @classmethod
    def _get_current_theme_colors(cls) -> Dict[str, str]:
        """Get all current theme colors as a dictionary."""
        theme_colors = {}
        for attr_name in dir(Colors):
            if not attr_name.startswith('_') and hasattr(Colors, attr_name):
                value = getattr(Colors, attr_name)
                if isinstance(value, str) and value:  # Non-empty string values
                    theme_colors[attr_name] = value
        return theme_colors
    
    @classmethod
    def _adjust_color(cls, color: str, brightness: float = 1.0, saturation: float = 1.0) -> str:
        """Adjust color brightness and saturation."""
        # Simple RGB adjustment for now
        hex_color = color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Apply brightness
        r = int(r * brightness)
        g = int(g * brightness)
        b = int(b * brightness)
        
        # Clamp values
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @classmethod
    def create_context_widget(cls, parent: tk.Widget, context: ThemeContext, 
                            widget_class: type, **kwargs) -> tk.Widget:
        """Create a widget with context-aware theming."""
        context_colors = cls.get_context_colors(context)
        
        # Apply context colors to widget kwargs
        themed_kwargs = kwargs.copy()
        
        if 'bg' in context_colors:
            themed_kwargs['bg'] = context_colors['bg']
        if 'fg' in context_colors and 'fg' not in themed_kwargs:
            themed_kwargs['fg'] = context_colors['fg']
        
        # Create widget with themed colors
        widget = widget_class(parent, **themed_kwargs)
        
        # Store context information for future updates
        widget._theme_context = context
        widget._original_colors = themed_kwargs.copy()
        
        return widget


class AdaptiveWidget:
    """Base class for widgets that can adapt to theme and context changes."""
    
    def __init__(self):
        self._context = ThemeContext.DEFAULT
        self._theme_dependencies = []
    
    def set_context(self, context: ThemeContext):
        """Set the theme context for this widget."""
        self._context = context
        self._apply_context_theming()
    
    def register_theme_dependency(self, color_attr: str):
        """Register a color attribute that should be updated on theme change."""
        if color_attr not in self._theme_dependencies:
            self._theme_dependencies.append(color_attr)
    
    def update_theme(self):
        """Update widget theming when theme changes."""
        self._apply_context_theming()
        self._update_dependent_colors()
    
    def _apply_context_theming(self):
        """Apply theming based on current context."""
        context_colors = ContextThemeResolver.get_context_colors(self._context)
        
        # Apply background
        if hasattr(self, 'configure'):
            if 'bg' in context_colors:
                try:
                    self.configure(bg=context_colors['bg'])
                except tk.TclError:
                    pass  # Widget might not support bg configuration
    
    def _update_dependent_colors(self):
        """Update colors that were registered as theme dependencies."""
        for color_attr in self._theme_dependencies:
            if hasattr(Colors, color_attr):
                try:
                    color_value = getattr(Colors, color_attr)
                    if hasattr(self, 'configure') and isinstance(color_value, str):
                        self.configure(**{color_attr.lower(): color_value})
                except (tk.TclError, AttributeError):
                    pass  # Widget might not support this color


class ThemedButton(AdaptiveWidget, tk.Button):
    """Button that automatically adapts to theme and context changes."""
    
    def __init__(self, parent, text: str = "", context: ThemeContext = ThemeContext.BUTTON, **kwargs):
        # Initialize parent classes
        AdaptiveWidget.__init__(self)
        tk.Button.__init__(self, parent, text=text, **kwargs)
        
        # Set up theming
        self.set_context(context)
        self._setup_theme_tracking()
    
    def _setup_theme_tracking(self):
        """Set up automatic theme change tracking."""
        self.register_theme_dependency('BUTTON_PRIMARY_BG')
        self.register_theme_dependency('BUTTON_PRIMARY_HOVER')
        self.register_theme_dependency('TEXT_PRIMARY')
        
        # Bind to theme change events (would be implemented in a full system)
        # For now, we'll rely on manual updates
    
    def set_hover_state(self, is_hover: bool):
        """Set hover state and apply appropriate styling."""
        if is_hover:
            hover_color = Colors.BUTTON_PRIMARY_HOVER
            if hover_color:
                try:
                    self.configure(bg=hover_color)
                except tk.TclError:
                    pass
        else:
            normal_color = Colors.BUTTON_PRIMARY_BG
            if normal_color:
                try:
                    self.configure(bg=normal_color)
                except tk.TclError:
                    pass


class ThemedFrame(AdaptiveWidget, tk.Frame):
    """Frame that automatically adapts to theme and context changes."""
    
    def __init__(self, parent, context: ThemeContext = ThemeContext.DEFAULT, **kwargs):
        # Initialize parent classes
        AdaptiveWidget.__init__(self)
        
        # Get context colors for initial setup
        context_colors = ContextThemeResolver.get_context_colors(context)
        themed_kwargs = kwargs.copy()
        
        if 'bg' in context_colors:
            themed_kwargs['bg'] = context_colors['bg']
        
        tk.Frame.__init__(self, parent, **themed_kwargs)
        self.set_context(context)
    
    def set_selected_state(self, is_selected: bool):
        """Set selected state and apply appropriate styling."""
        if is_selected:
            selected_color = getattr(Colors, 'SURFACE_SELECTED', None)
            if selected_color:
                try:
                    self.configure(bg=selected_color)
                except tk.TclError:
                    pass
        else:
            # Reset to context background
            self._apply_context_theming()


# Default context theme definitions
def register_default_context_themes():
    """Register default context theme overrides."""
    
    # Dialog context - slightly elevated appearance
    ContextThemeResolver.register_context_override(ThemeContext.DIALOG, {
        "bg": "SURFACE_RAISED",
        "border": "BORDER",
    })
    
    # Modal context - darker overlay
    ContextThemeResolver.register_context_override(ThemeContext.MODAL, {
        "bg": "SURFACE_ALT",
    })
    
    # Input context - focused appearance
    ContextThemeResolver.register_context_override(ThemeContext.INPUT, {
        "bg": "SURFACE_RAISED",
        "fg": "TEXT_PRIMARY",
    })
    
    # Card context - elevated content area
    ContextThemeResolver.register_context_override(ThemeContext.CARD, {
        "bg": "CARD_PANEL_BG",
        "border": "CARD_PANEL_BORDER",
    })
    
    # Error state context
    ContextThemeResolver.register_context_override(ThemeContext.ERROR_STATE, {
        "bg": "STATE_ERROR",
        "fg": "SURFACE",
    })
    
    # Success state context
    ContextThemeResolver.register_context_override(ThemeContext.SUCCESS_STATE, {
        "bg": "STATE_SUCCESS",
        "fg": "SURFACE",
    })
    
    # Warning state context
    ContextThemeResolver.register_context_override(ThemeContext.WARNING_STATE, {
        "bg": "STATE_WARNING",
        "fg": "SURFACE",
    })


# Initialize default themes
register_default_context_themes()