"""
frames package
--------------
Contains all UI frame and tab classes for the LoRa Chat desktop app.
"""

from .login_frame import LoginFrame
from .main_frame import MainFrame
from .chat_tab import ChatTab
from .settings_tab import SettingsTab

__all__ = ["LoginFrame", "MainFrame", "ChatTab", "SettingsTab"]
