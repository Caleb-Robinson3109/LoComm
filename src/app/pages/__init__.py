"""
frames package
--------------
Contains all UI frame and tab classes for the LoRa Chat desktop app.
"""

from .main_frame import MainFrame
from .settings_page import SettingsPage
from .home_page import HomePage
from .chatroom_page import ChatroomPage, PairPage
from .sidebar import Sidebar
from .view_manager import ViewManager

__all__ = ["MainFrame", "SettingsPage", "HomePage",
           "ChatroomPage", "PairPage", "Sidebar", "ViewManager"]
