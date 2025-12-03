# LoComm Desktop App

This desktop UI wraps the LoComm device API for pairing, messaging, and device setup.

## Quick Start
- Install Python 3.11+ and required packages (see project root instructions).
- From the repo root run: `python -m src.app.app`.
- The window opens centered in a compact “Login” layout; it expands after login.

## Authentication Flow
- **Register (Set Password):** On the login page click `Register` to open the modal. Enter and confirm a password (3–32 chars). The app sends `reset_passoword(...)` to the device. On success the password field is prefilled and validation runs.
- **Validate Password:** Enter the device password and click `Validate`. The app calls `enter_password(...)`. When accepted, the “Preferred Name” field unlocks and you can proceed.
- **Login:** After validation, enter a display name (sent to the device via `store_name_on_device(...)`) and click `Login` to enter the main shell.

## Main Shell
- **Home:** Landing view after login with device status and quick actions.
- **Pair/Chatroom:** Access pairing modal when needed; chat features are currently disabled in UI but transport/session remain active.
- **Theme Toggle:** Switch between light/dark; the app recreates the main frame to apply styles.

## Session & Transport
- The app bootstraps `AppController` for business logic and connects to the device on launch (deviceless mode can be toggled in code for testing).
- On logout or window close the controller stops the transport session and clears UI state.

## Troubleshooting
- Password rejected: ensure length 3–32 and retry Validate; use Register to reset if needed.
- Device not detected: reconnect hardware, then restart the app to re-init transport.
- UI unresponsive after modal: close secondary windows first (Register modal grabs focus).
