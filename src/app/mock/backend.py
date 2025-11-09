"""
Mock LoRa transport backend used for local development and demos.

This module is intentionally isolated so it can be removed in production
builds once the hardware transport is ready.
"""
from __future__ import annotations

import random
import time
from typing import Optional

from mock.device_service import MockDevice, get_mock_device_service
from mock.network_simulator import LoRaNetworkSimulator
from mock.peer_bridge import get_peer_bridge
from services.transport_contract import PairingContext, TransportMessage


class MockLoCommBackend:
    """Simple in-memory backend that simulates a LoRa link."""

    label = "mock"

    def __init__(self):
        self._connected = False
        self._active_device: Optional[MockDevice] = None
        self._message_counter = 0
        self._device_service = get_mock_device_service()
        self._network = LoRaNetworkSimulator()
        self._bridge = get_peer_bridge()
        self._bridge.register_backend(self)

    def connect(self, pairing_context: Optional[PairingContext] = None) -> bool:
        """
        Pretend to connect to a device.

        Args:
            pairing_context: Optional metadata coming from the UI.
        """
        self._connected = True
        scenario = "default"
        device_id = None
        provided_name = None
        if pairing_context:
            scenario = pairing_context.metadata.get("scenario", "default")
            device_id = pairing_context.device_id
            provided_name = pairing_context.device_name

        self._network.set_scenario(scenario)
        self._bridge.register_backend(self)
        self._active_device = None
        if device_id:
            self._active_device = self._device_service.get_device(device_id)
        if self._active_device is None and provided_name:
            self._active_device = MockDevice(
                device_id=device_id or "MOCK",
                name=provided_name,
                status="Available",
                last_seen="Just paired",
                metadata={"source": pairing_context.mode if pairing_context else "mock"},
                telemetry={"rssi": -70, "snr": 4.0, "battery": 80},
            )
        if self._active_device is None:
            self._active_device = self._device_service.pick_default()
        if self._active_device and provided_name:
            self._active_device.name = provided_name

        self._seed_handshake()
        return True

    def disconnect(self) -> bool:
        self._connected = False
        self._active_device = None
        self._message_counter = 0
        self._bridge.unregister_backend(self)
        return True

    def send(self, message: TransportMessage) -> bool:
        if not self._connected:
            return False

        self._message_counter += 1
        self._bridge.notify_peer(message.sender or "Desktop", message.payload)
        return True

    def receive(self) -> Optional[TransportMessage]:
        if not self._connected:
            time.sleep(0.2)
            return None

        message = self._network.next_message()
        if message:
            return message

        # Heartbeat disabled for cleaner mock conversations
        # if random.random() < 0.05:
        #     self._queue_heartbeat()
        time.sleep(0.2)
        return None

    def start_pairing(self) -> bool:
        return True

    def stop_pairing(self) -> bool:
        return True

    def _seed_handshake(self):
        if not self._active_device:
            return
        metadata = {
            "scenario": self._network.scenario.name,
            "rssi": self._active_device.telemetry.get("rssi", -78),
            "snr": self._active_device.telemetry.get("snr", 4.2),
            "battery": self._active_device.telemetry.get("battery", 80),
        }
        text = (
            f"{self._active_device.name} ready. Firmware "
            f"{self._active_device.metadata.get('firmware', '1.0.0')}"
        )
        self._emit_system_message(text, metadata)
        self._bridge.notify_peer("System", text)

    def _queue_heartbeat(self):
        return  # Heartbeats disabled for mock testing

    def inject_peer_message(self, text: str) -> None:
        if not self._connected or not self._active_device:
            return
        telemetry = self._active_device.telemetry or {}
        metadata = {
            "scenario": self._network.scenario.name,
            "rssi": telemetry.get("rssi", -78),
            "snr": telemetry.get("snr", 4.0),
            "battery": telemetry.get("battery", 80),
        }
        message = TransportMessage(
            sender=self._active_device.name,
            payload=text,
            metadata=metadata,
        )
        self._network.queue_message(message)

    def _emit_system_message(self, text: str, metadata: Optional[dict] = None):
        payload_metadata = metadata or {
            "scenario": self._network.scenario.name,
            "rssi": -78,
            "snr": 4.0,
            "battery": 80,
        }
        message = TransportMessage(
            sender="System",
            payload=text,
            metadata=payload_metadata,
        )
        self._network.queue_message(message)
