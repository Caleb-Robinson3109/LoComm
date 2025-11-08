# Transport Contract & Handshake

The desktop UI talks to the transport layer exclusively through the
`services.transport_contract` dataclasses and the `TransportBackend` protocol.
This file documents the expectations so the hardware/network team can plug in a
real LoRa stack without touching UI code.

## Message & Status Schemas

| Dataclass | Fields | Notes |
|-----------|--------|-------|
| `PairingContext` | `device_id`, `device_name`, `mode` (`pin|demo|mock|hardware`), `metadata` | Supplied on `connect()` to describe how the desktop expects to pair. |
| `TransportMessage` | `sender`, `payload`, `timestamp`, `metadata` | Used for *both* outbound and inbound LoRa frames. `metadata` can include RSSI, SNR, channel, hop, encryption flags, etc. |
| `TransportStatus` | `text`, `level`, `detail` | Optional helper for structured status updates. Current UI consumes text-only but `level` is ready for richer UX. |

All future backends **must** implement the `TransportBackend` protocol exposed
in `services.transport_registry`.

## Handshake Flow (LoRa Pairing)

1. **Pairing Context Construction**  
   The UI builds a `PairingContext` when the user selects a device and enters a
   secure PIN. Metadata includes the requested profile (`LOCOMM_TRANSPORT_PROFILE`)
   so the backend can decide whether to honor mock/demo behavior or talk to real
   radios.

2. **`connect(context)`**  
   - Backend starts LoRa discovery/pairing.  
   - Must block until handshake succeeds or fails.  
   - Should validate the PIN/auth challenge before reporting success.  
   - Emit `TransportStatus` updates such as “Scanning”, “Awaiting PIN”,
     “Link established”, etc.

3. **ACK & Retry Expectations**  
   - Every outbound `TransportMessage` represents a single LoRa frame.  
   - Backends should implement at-least-once delivery with ACK/NAK semantics.
     If the radio provides no ACK, emulate one in software (retry 3 times with
     exponential backoff: 250 ms, 500 ms, 1 s).  
   - Populate `metadata["attempt"]` and `metadata["rssi"]` when available so the
     UI can surface diagnostics.

4. **Receive Loop**  
   - Backend returns `TransportMessage` objects from `receive()`.  
   - Empty queues should return `None` so the adapter can sleep.  
   - Include raw payload plus any decoded telemetry in `metadata`.

5. **Disconnect Semantics**  
   - `disconnect()` must tear down timers, threads, and radio state.  
   - Always emit a final status (`Disconnected`, `Connection error`, etc.) so
     the shared `StatusManager` can keep UI components in sync.

## Runtime Swapping

Developers set the environment variable `LOCOMM_TRANSPORT_PROFILE` (or add it to
`~/.locomm/runtime.json`) to choose a backend:

| Profile | Description |
|---------|-------------|
| `auto` (default) | Try `locomm` first, fall back to `mock`. |
| `locomm` | Hardware/API-backed transport exposed by the network team. |
| `mock` | In-memory echo backend for UI work and unit tests. |

The selected profile is logged on startup (`~/.locomm/locomm.log`) and exposed
via `LoCommTransport.profile` so UI diagnostics can surface it.

## Status Mapping

Status text emitted by the backend feeds the consolidated `StatusManager`, which
maps keywords to UI badges. Prefer the following verb set to keep things
consistent:

| Stage | Recommended Status Text |
|-------|-------------------------|
| Discovery | “Scanning for devices…” |
| PIN exchange | “Awaiting PIN”, “Verifying PIN” |
| Secure link | “Connecting to {device}…”, “Connected (LoRa)” |
| Errors | “Connection failed”, “Authentication error”, “Link lost” |
| Disconnect | “Disconnected”, “Peer closed link” |

Keeping to these verbs ensures the Home, Devices, Sidebar, and Chat views remain
in sync without additional wiring.
