import time

from mock.backend import MockLoCommBackend
from services.transport_contract import PairingContext, TransportMessage


def test_mock_backend_round_trip():
    backend = MockLoCommBackend()
    ctx = PairingContext(device_id="DEV001", device_name="Device Alpha", mode="mock", metadata={"scenario": "demo"})
    assert backend.connect(ctx)

    outbound = TransportMessage(sender="Tester", payload="Hello")
    assert backend.send(outbound)

    deadline = time.time() + 2
    while time.time() < deadline:
        incoming = backend.receive()
        if incoming:
            assert incoming.sender
            assert incoming.payload
            assert isinstance(incoming.metadata, dict)
            break
        time.sleep(0.1)
    else:
        raise AssertionError("No response received from mock backend")

    assert backend.disconnect()
