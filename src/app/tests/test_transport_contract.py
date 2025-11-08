from services.transport_contract import PairingContext, TransportMessage, TransportStatus, TransportStatusLevel


def test_pairing_context_defaults():
    ctx = PairingContext(device_id="DEV123", device_name="Demo")
    assert ctx.mode == "pin"
    assert ctx.metadata == {}


def test_transport_message_roundtrip():
    message = TransportMessage(sender="Alice", payload="Hello", metadata={"foo": "bar"})
    snapshot = message.to_dict()
    rebuilt = TransportMessage.from_dict(snapshot)
    assert rebuilt.sender == "Alice"
    assert rebuilt.payload == "Hello"
    assert rebuilt.metadata["foo"] == "bar"


def test_transport_status_levels():
    status = TransportStatus(text="Connected", level=TransportStatusLevel.SUCCESS)
    assert status.level == TransportStatusLevel.SUCCESS
