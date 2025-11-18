"""
frames package
--------------
Contains all UI frame and tab classes for the LoRa Chat desktop app.
"""

from .main_page import MainPage
from .settings_page import SettingsPage
from .home_page import HomePage
from .peers_page import PeersPage, PairPage
from .sidebar_page import SidebarPage
from .view_manager import ViewManager

__all__ = ["MainPage", "SettingsPage", "HomePage",
           "PeersPage", "PairPage", "SidebarPage", "ViewManager"]
