"""
frames package
--------------
Contains all UI frame and tab classes for the LoRa Chat desktop app.
"""

from .pin_pairing_frame import PINPairingFrame
from .main_frame import MainFrame
from .settings_page import SettingsPage
from .home_page import HomePage
from .pair_page import PairPage
from .chat_page import ChatPage
from .about_page import AboutPage
from .sidebar import Sidebar
from .view_manager import ViewManager

__all__ = ["PINPairingFrame", "MainFrame", "SettingsPage", "HomePage",
           "PairPage", "ChatPage", "AboutPage", "Sidebar", "ViewManager"]
