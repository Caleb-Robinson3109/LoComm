"""
frames package
--------------
Contains all UI frame and tab classes for the LoRa Chat desktop app.
"""

from .main_frame import MainFrame
from .settings_page import SettingsPage
from .home_page import HomePage
from .peers_page import PeersPage, PairPage
from .sidebar import Sidebar
from .view_manager import ViewManager

__all__ = ["MainFrame", "SettingsPage", "HomePage",
           "PeersPage", "PairPage", "Sidebar", "ViewManager"]
