"""View management system for proper lifecycle handling of application views."""
import tkinter as tk
from typing import Dict, Any, Optional, Set, List
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

        # Simple cache of recently used views
        self._cache_limit = 3
        self._cache_order: List[str] = []
        self._protected_views: Set[str] = {"home"}

    def register_view(
        self,
        view_name: str,
        container: tk.Frame,
        component: Any = None,
        *,
        pack_options: Optional[dict] = None,
    ):
        """
        Register a view with the view manager.

        Args:
            view_name: Unique identifier for the view
            container: Frame that contains the view
            component: Main component for the view (optional)
            pack_options: Options forwarded to container.pack when showing
        """
        self.view_containers[view_name] = container
        if component is not None:
            self.view_components[view_name] = component
        if pack_options is not None:
            self.view_pack_options[view_name] = pack_options

        self.logger.debug(f"Registered view '{view_name}'")

    def attach_component(self, view_name: str, component: Any):
        """
        Attach or replace the component associated with a view without
        recreating the container. Useful for lazy loaded views.

        Args:
            view_name: Registered view identifier
            component: Component instance associated with the view
        """
        if view_name not in self.view_containers:
            raise ValueError(f"Cannot attach component for unregistered view '{view_name}'")

        self.view_components[view_name] = component
        self.logger.debug(f"Attached component for view '{view_name}'")

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

        self.logger.debug(
            f"Switching view from '{previous_view}' to '{view_name}' "
            f"(same_view={is_same_view})"
        )

        # Call on_hide on previous component if it exists and view is changing
        if previous_view and not is_same_view:
            prev_component = self.view_components.get(previous_view)
            if prev_component and hasattr(prev_component, "on_hide"):
                try:
                    prev_component.on_hide()
                except Exception as e:
                    self.logger.warning(
                        f"Error during on_hide for view '{previous_view}': {e}"
                    )

        # Hide all view containers
        for name, container in self.view_containers.items():
            container.pack_forget()

        # Show the requested view container
        container = self.view_containers[view_name]
        pack_opts = self.view_pack_options.get(
            view_name,
            {"fill": tk.BOTH, "expand": True},
        )
        container.pack(**pack_opts)

        # Update active view and cache order
        self.active_view = view_name
        self._record_cache_usage(view_name)
        self._trim_cache()

        # Call on_show on the new component only if the view actually changed
        if not is_same_view:
            component = self.view_components.get(view_name)
            if component and hasattr(component, "on_show"):
                try:
                    component.on_show()
                except Exception as e:
                    self.logger.warning(
                        f"Error during on_show for view '{view_name}': {e}"
                    )

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

    def detach_component(self, view_name: str):
        """
        Remove the component associated with a view while keeping its container.
        This frees memory but preserves layout wiring.
        """
        component = self.view_components.pop(view_name, None)
        if not component:
            return

        self.logger.debug(f"Detaching component for view '{view_name}'")

        # Give the component a chance to hide and then destroy it
        try:
            if hasattr(component, "on_hide"):
                component.on_hide()
        except Exception as exc:
            self.logger.warning(
                f"Error during on_hide for detached view '{view_name}': {exc}"
            )
        try:
            if hasattr(component, "destroy"):
                component.destroy()
        except Exception as exc:
            self.logger.warning(
                f"Error destroying detached view '{view_name}': {exc}"
            )

    def set_cache_limit(self, limit: int):
        """Set maximum number of non protected views kept alive in memory."""
        self._cache_limit = max(0, int(limit))

    def set_protected_views(self, views: Set[str]):
        """Set which views should never be evicted from the cache."""
        self._protected_views = set(views)

    def _record_cache_usage(self, view_name: str):
        """Move view_name to the end of the LRU list."""
        if view_name in self._cache_order:
            self._cache_order.remove(view_name)
        self._cache_order.append(view_name)
        self.logger.debug(f"Cache usage recorded for '{view_name}': {self._cache_order}")

    def _trim_cache(self):
        """
        Enforce the cache limit by detaching least recently used views that are
        not active and not protected.
        """
        while len(self._cache_order) > self._cache_limit:
            candidates = [
                view
                for view in self._cache_order
                if view != self.active_view and view not in self._protected_views
            ]
            if not candidates:
                break

            target = candidates[0]
            self._cache_order.remove(target)
            self.logger.debug(
                f"Trimming cache: detaching view '{target}', "
                f"remaining cache: {self._cache_order}"
            )
            self.detach_component(target)
