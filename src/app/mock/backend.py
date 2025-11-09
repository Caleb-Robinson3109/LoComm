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

    def connect(self, pairing_context: Optional[PairingContext] = None) -> bool:
        """
        Pretend to connect to a device.

        Args:
            pairing_context: Optional metadata coming from the UI.
        """
        self._connected = True
        scenario = "default"
        device_id = None
        if pairing_context:
            scenario = pairing_context.metadata.get("scenario", "default")
            device_id = pairing_context.device_id

        self._network.set_scenario(scenario)
        self._active_device = None
        if device_id:
            self._active_device = self._device_service.get_device(device_id)
        if self._active_device is None:
            self._active_device = self._device_service.pick_default()

        self._seed_handshake()
        return True

    def disconnect(self) -> bool:
        self._connected = False
        self._active_device = None
        self._message_counter = 0
        return True

    def send(self, message: TransportMessage) -> bool:
        if not self._connected:
            return False

        peer_name = self._active_device.name if self._active_device else "Mock Device"
        telemetry = (self._active_device.telemetry if self._active_device else {}) or {}
        metadata = {
            "scenario": self._network.scenario.name,
            "attempt": self._message_counter + 1,
            "rssi": telemetry.get("rssi", -80),
            "snr": telemetry.get("snr", 4.0),
            "battery": telemetry.get("battery", 75),
        }
        self._message_counter += 1
        response_text = self._build_response_text(message.payload)
        response = TransportMessage(
            sender=peer_name,
            payload=response_text,
            metadata=metadata,
        )
        self._network.queue_message(response)
        return True

    def receive(self) -> Optional[TransportMessage]:
        if not self._connected:
            time.sleep(0.2)
            return None

        message = self._network.next_message()
        if message:
            return message

        if random.random() < 0.05:
            self._queue_heartbeat()
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
        message = TransportMessage(
            sender=self._active_device.name,
            payload=f"{self._active_device.name} ready. Firmware {self._active_device.metadata.get('firmware', '1.0.0')}",
            metadata=metadata,
        )
        self._network.queue_message(message)

    def _queue_heartbeat(self):
        if not self._active_device:
            return
        heartbeat = TransportMessage(
            sender=self._active_device.name,
            payload="Heartbeat ping",
            metadata={
                "scenario": self._network.scenario.name,
                "heartbeat": True,
                "rssi": self._active_device.telemetry.get("rssi", -78),
                "snr": self._active_device.telemetry.get("snr", 4.2),
            }
        )
        self._network.queue_message(heartbeat)

    def _build_response_text(self, payload: str) -> str:
        if not payload:
            return "ACK"

        # Special handling for Mock device communication
        if self._active_device and self._active_device.device_id == "MOCK":
            # Mock device responds with technical/analytical responses
            if "hello" in payload.lower() or "hi" in payload.lower():
                return "Mock device online. Ready for testing protocols."
            elif "status" in payload.lower():
                return f"Mock status: Connected, RSSI={self._active_device.telemetry.get('rssi', -25)}dBm, Battery={self._active_device.telemetry.get('battery', 100)}%"
            elif "test" in payload.lower():
                return "Test message received. Echoing back: " + payload
            elif "ping" in payload.lower():
                return "Pong! Mock device responding."
            else:
                return f"Mock received: '{payload}' (length: {len(payload)} chars)"

        # Default echo behavior for other devices
        if len(payload) < 40:
            return f"Echo: {payload}"
        return f"ACK ({len(payload)} bytes)"
