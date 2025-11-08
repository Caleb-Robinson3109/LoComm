#!/usr/bin/env python3
"""
End-to-end mock workflow runner.
Simulates a pairing + message exchange using the MockLoCommBackend so
developers can verify transport behavior without launching the GUI.
"""
from __future__ import annotations

import json
import time

from mock.backend import MockLoCommBackend
from services.transport_contract import PairingContext, TransportMessage


def run_workflow(device_id: str = "DEV001", scenario: str = "demo") -> None:
    backend = MockLoCommBackend()
    context = PairingContext(
        device_id=device_id,
        device_name=f"Mock device {device_id}",
        mode="mock",
        metadata={"scenario": scenario},
    )
    print(f"[workflow] Connecting to {context.device_name} via scenario '{scenario}'")
    backend.connect(context)

    outbound = TransportMessage(sender="Workflow", payload="Hello from workflow runner!")
    backend.send(outbound)
    print("[workflow] Sent:", outbound.payload)

    deadline = time.time() + 5
    while time.time() < deadline:
        incoming = backend.receive()
        if incoming:
            print("[workflow] Received message:")
            print(json.dumps(incoming.to_dict(), indent=2))
            break
        time.sleep(0.1)
    else:
        print("[workflow] No response received within 5 seconds.")

    backend.disconnect()
    print("[workflow] Done.")


if __name__ == "__main__":
    run_workflow()
