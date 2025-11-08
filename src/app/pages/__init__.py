"""
frames package
--------------
Contains all UI frame and tab classes for the LoRa Chat desktop app.
"""

from .pin_pairing_frame import PINPairingFrame
from .main_frame import MainFrame
from .settings_page import SettingsPage
from .home_page import HomePage
from .devices_page import DevicesPage, PairPage
from .chat_page import ChatPage
from .sidebar import Sidebar
from .view_manager import ViewManager

__all__ = ["PINPairingFrame", "MainFrame", "SettingsPage", "HomePage",
           "DevicesPage", "PairPage", "ChatPage", "Sidebar", "ViewManager"]
