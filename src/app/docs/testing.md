# Testing & Verification

This document summarizes the new test coverage and the recommended steps for
verifying the mock transport stack before shipping UI work.

## Automated Tests

| Test | Purpose |
|------|---------|
| `tests/test_transport_contract.py` | Ensures the PairingContext/TransportMessage/TransportStatus dataclasses serialize and deserialize cleanly so the transport adapter and backend stay in lockstep. |
| `tests/test_mock_transport.py` | Exercises the MockLoCommBackend end-to-end, verifying that a message sent via `send()` produces a response within 2 seconds using the network simulator queue. |

Run them with:

```bash
python3 -m pytest tests/test_transport_contract.py tests/test_mock_transport.py
```

## Manual Workflow

1. Launch the desktop app with `LOCOMM_TRANSPORT_PROFILE=mock python3 app.py`.
2. Open **Devices & Trust** → pick a mock device → enter a PIN via the modal.
3. Switch scenarios using the dropdown; telemetry readings in the sidebar update
   immediately.
4. Send and receive a few chat messages; open **Settings → Diagnostics** to view
   the JSON log of events or export it to a file.

For quick CLI verification without the UI, run:

```bash
python3 mock/workflow.py
```

It will pair using the mock backend, send a message, and dump the response +
metadata to stdout.
