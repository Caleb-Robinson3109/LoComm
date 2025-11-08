"""
Dependency Injection Container for LoRa Chat Application.
Provides a centralized way to manage and resolve dependencies.
"""
from typing import Any, Callable, Dict, Type, Optional
import weakref


class DependencyContainer:
    """
    Simple dependency injection container that manages object creation
    and dependency resolution across the application.
    """

    def __init__(self):
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
        self._weak_refs: Dict[str, weakref.WeakReference] = {}

    def register_factory(self, interface: Type, factory: Callable, singleton: bool = False):
        """
        Register a factory function for creating instances of an interface.

        Args:
            interface: The interface/class type to register
            factory: Factory function that creates instances
            singleton: If True, creates only one instance
        """
        self._factories[interface] = (factory, singleton)

    def register_instance(self, interface: Type, instance: Any):
        """
        Register a specific instance for an interface.

        Args:
            interface: The interface/class type
            instance: The instance to register
        """
        self._singletons[interface] = instance

    def resolve(self, interface: Type) -> Any:
        """
        Resolve a dependency from the container.

        Args:
            interface: The interface/class type to resolve

        Returns:
            An instance of the requested type

        Raises:
            ValueError: If the interface is not registered
        """
        # Check for direct singleton instance
        if interface in self._singletons:
            return self._singletons[interface]

        # Check for factory
        if interface not in self._factories:
            raise ValueError(f"Interface {interface} not registered in container")

        factory, is_singleton = self._factories[interface]

        # Create instance
        instance = factory()

        # Store as singleton if needed
        if is_singleton:
            self._singletons[interface] = instance

        return instance

    def clear_singletons(self):
        """Clear all registered singleton instances."""
        self._singletons.clear()

    def reset(self):
        """Reset the entire container."""
        self._factories.clear()
        self._singletons.clear()
        self._weak_refs.clear()


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container instance."""
    global _container
    if _container is None:
        _container = DependencyContainer()
        _setup_default_dependencies(_container)
    return _container


def _setup_default_dependencies(container: DependencyContainer):
    """
    Set up default dependencies in the container.
    This replaces direct instantiation with dependency injection.
    """
    from utils.connection_manager import ConnectionManager
    from utils.status_manager import StatusManager
    from utils.mock_config import MockConfig, get_mock_config
    from utils.runtime_settings import RuntimeSettings, get_runtime_settings

    # Register managers as singletons
    container.register_factory(ConnectionManager,
                              lambda: ConnectionManager(),
                              singleton=True)
    container.register_factory(StatusManager,
                              lambda: StatusManager(),
                              singleton=True)
    container.register_factory(RuntimeSettings,
                              lambda: get_runtime_settings(),
                              singleton=True)
    container.register_factory(MockConfig,
                              lambda: get_mock_config(),
                              singleton=True)


def inject_dependencies(**dependencies):
    """
    Decorator for automatic dependency injection.

    Usage:
        @inject_dependencies(connection_manager=ConnectionManager)
        def __init__(self, connection_manager):
            self.connection_manager = connection_manager
    """
    def decorator(cls_or_func):
        if callable(cls_or_func) and hasattr(cls_or_func, '__init__'):
            # Class decorator
            original_init = cls_or_func.__init__

            def new_init(self, *args, **kwargs):
                # Inject dependencies
                for name, interface in dependencies.items():
                    if name not in kwargs:
                        container = get_container()
                        kwargs[name] = container.resolve(interface)

                original_init(self, *args, **kwargs)

            cls_or_func.__init__ = new_init
            return cls_or_func
        else:
            # Function decorator
            def wrapper(*args, **kwargs):
                container = get_container()
                for name, interface in dependencies.items():
                    if name not in kwargs:
                        kwargs[name] = container.resolve(interface)
                return cls_or_func(*args, **kwargs)
            return wrapper
    return decorator
