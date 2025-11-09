"""Modernized Home page built on the refreshed design system."""
from __future__ import annotations

import tkinter as tk

from utils.design_system import Colors, DesignUtils, Spacing, Typography
from utils.ui_helpers import create_scroll_container
from utils.ui_store import DeviceStage, DeviceStatusSnapshot, get_ui_store
from .base_page import BasePage, PageContext


class HomePage(BasePage):
    """Conversation hub that mirrors Signal-style first run experience."""

    def __init__(self, master, context: PageContext):
        super().__init__(master, context=context, bg=Colors.SURFACE)
        self.app = context.app if context else None
        self.session = context.session if context else None
        self.host = context.navigator if context else None
        self.ui_store = get_ui_store()
        self._device_subscription = None

        self.connection_title_var = tk.StringVar(value="No device paired")
        self.connection_subtitle_var = tk.StringVar(value="Start by pairing a LoRa contact to open a secure chat.")
        self.connection_badge_var = tk.StringVar(value="Disconnected")
        self.connection_detail_var = tk.StringVar(value="Awaiting secure PIN handoff")

        scroll = create_scroll_container(self, bg=Colors.SURFACE, padding=(0, Spacing.LG))
        body = scroll.frame

        DesignUtils.hero_header(
            body,
            title="Secure conversations, Signal-level polish",
            subtitle="Pair LoRa hardware, verify trust, and jump back into chats from a single dashboard.",
            actions=[]
        )
        # Apply the latest snapshot immediately so the UI reflects the current store state.
        self._apply_snapshot(self.ui_store.get_device_status())

    def on_show(self):
        """Start listening to store updates when the page is visible."""
        self._subscribe_to_store()

    def on_hide(self):
        """Stop expensive updates when the page is hidden."""
        self._unsubscribe_from_store()

    # ------------------------------------------------------------------ #
    def _subscribe_to_store(self):
        if self._device_subscription is not None:
            return

        def _callback(snapshot: DeviceStatusSnapshot):
            self._handle_device_snapshot(snapshot)

        self._device_subscription = _callback
        self.ui_store.subscribe_device_status(_callback)

    def _unsubscribe_from_store(self):
        if self._device_subscription is None:
            return
        self.ui_store.unsubscribe_device_status(self._device_subscription)
        self._device_subscription = None

    def _handle_device_snapshot(self, snapshot: DeviceStatusSnapshot):
        self._apply_snapshot(snapshot)

    def _apply_snapshot(self, snapshot: DeviceStatusSnapshot | None):
        if snapshot is None:
            return
        badge_text, badge_color = self._badge_style_for_stage(snapshot.stage)
        self.connection_badge_var.set(badge_text)
        self.connection_title_var.set(snapshot.title)
        self.connection_subtitle_var.set(snapshot.subtitle)
        self.connection_detail_var.set(snapshot.detail)
        # badge removed from UI

    @staticmethod
    def _badge_style_for_stage(stage: DeviceStage) -> tuple[str, str]:
        mapping = {
            DeviceStage.READY: ("Ready", Colors.STATE_INFO),
            DeviceStage.SCANNING: ("Scanning", Colors.STATE_INFO),
            DeviceStage.AWAITING_PIN: ("Awaiting PIN", Colors.STATE_WARNING),
            DeviceStage.CONNECTING: ("Connecting", Colors.STATE_INFO),
            DeviceStage.CONNECTED: ("Connected", Colors.STATE_SUCCESS),
            DeviceStage.DISCONNECTED: ("Disconnected", Colors.STATE_ERROR),
        }
        return mapping.get(stage, mapping[DeviceStage.READY])

    def destroy(self):
        self._unsubscribe_from_store()
        return super().destroy()
