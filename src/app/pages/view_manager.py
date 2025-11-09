"""View management system for proper lifecycle handling of application views."""
import tkinter as tk
from typing import Dict, Any, Optional
from utils.app_logger import get_logger


class ViewManager:
    """
    Manages view lifecycle and switching between different application views.
    Provides proper memory management and state handling.
    """

    def __init__(self, parent_frame: tk.Misc):
        self.parent_frame = parent_frame
        self.active_view: Optional[str] = None
        self.view_containers: Dict[str, tk.Frame] = {}
        self.view_components: Dict[str, Any] = {}
        self.view_pack_options: Dict[str, dict] = {}
        self.logger = get_logger("view_manager")

    def register_view(self, view_name: str, container: tk.Frame, component: Any = None, *, pack_options: Optional[dict] = None):
        """
        Register a view with the view manager.

        Args:
            view_name: Unique identifier for the view
            container: Frame that contains the view
            component: Main component for the view (optional)
        """
        self.view_containers[view_name] = container
        if component:
            self.view_components[view_name] = component
        if pack_options:
            self.view_pack_options[view_name] = pack_options

    def attach_component(self, view_name: str, component: Any):
        """
        Attach or replace the component associated with a view without
        recreating the container. Useful for lazy-loaded views.

        Args:
            view_name: Registered view identifier.
            component: Component instance associated with the view.
        """
        if view_name not in self.view_containers:
            raise ValueError(f"Cannot attach component for unregistered view '{view_name}'")
        self.view_components[view_name] = component

    def show_view(self, view_name: str):
        """
        Show the specified view and hide all others.

        Args:
            view_name: Name of the view to show
        """
        if view_name not in self.view_containers:
            raise ValueError(f"View '{view_name}' not registered")

        previous_view = self.active_view
        is_same_view = previous_view == view_name

        if previous_view and not is_same_view:
            prev_component = self.view_components.get(previous_view)
            if prev_component and hasattr(prev_component, "on_hide"):
                try:
                    prev_component.on_hide()
                except Exception as e:
                    self.logger.warning(f"Error during on_hide for view '{previous_view}': {e}")

        # Hide all views first
        for container in self.view_containers.values():
            container.pack_forget()

        # Show the requested view
        container = self.view_containers[view_name]
        pack_opts = self.view_pack_options.get(view_name, {"fill": tk.BOTH, "expand": True})
        container.pack(**pack_opts)

        # Update active view
        self.active_view = view_name

        if not is_same_view:
            component = self.view_components.get(view_name)
            if component and hasattr(component, "on_show"):
                try:
                    component.on_show()
                except Exception as e:
                    self.logger.warning(f"Error during on_show for view '{view_name}': {e}")

    def get_active_view(self) -> Optional[str]:
        """Get the currently active view name."""
        return self.active_view

    def get_view_component(self, view_name: str) -> Any:
        """
        Get the component for a specific view.

        Args:
            view_name: Name of the view

        Returns:
            Component instance or None if not found
        """
        return self.view_components.get(view_name)

    def cleanup_view(self, view_name: str):
        """
        Clean up resources for a specific view.

        Args:
            view_name: Name of the view to clean up
        """
        # Clean up view components
        if view_name in self.view_components:
            component = self.view_components[view_name]
            # Call cleanup method if available
            if hasattr(component, 'cleanup'):
                try:
                    component.cleanup()
                except Exception as e:
                    # Log cleanup errors instead of silently ignoring
                    self.logger.warning(f"Error during component cleanup for view '{view_name}': {e}")
            del self.view_components[view_name]

        # Clean up view containers
        if view_name in self.view_containers:
            container = self.view_containers[view_name]
            # Destroy the container to free resources
            try:
                # Clear any child widgets first
                for child in container.winfo_children():
                    try:
                        child.destroy()
                    except Exception:
                        pass  # Ignore individual child destruction errors
                container.destroy()
            except Exception as e:
                # Log container destruction errors
                self.logger.warning(f"Error during container destruction for view '{view_name}': {e}")
            del self.view_containers[view_name]

    def cleanup_all(self):
        """Clean up all registered views."""
        for view_name in list(self.view_containers.keys()):
            self.cleanup_view(view_name)
        self.active_view = None
