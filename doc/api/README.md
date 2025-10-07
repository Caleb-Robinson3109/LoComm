# Device API

This API provides a set of functions for managing connections, authentication, and communication with an ESP-based device.

## Table of Contents
- [Connection Management](#connection-management)
- [Authentication](#authentication)
- [Messaging](#messaging)
- [Pairing](#pairing)

---

## Connection Management

### `connect_to_device() -> bool`
Connects to the device.

**Returns:**  
- `True` if the connection is successful.  
- `False` otherwise.

---

### `disconnect_from_device() -> bool`
Disconnects from the currently connected device.

**Returns:**  
- `True` if disconnection is successful.  
- `False` otherwise.

---

## Authentication

### `enter_password(password: str) -> bool`
Verifies the provided password against the one stored on the ESP.

**Parameters:**  
- `password`: The password string to authenticate with.

**Returns:**  
- `True` if the password is correct.  
- `False` otherwise.

---

### `set_password(old: str, new: str) -> bool`
Changes the device password.

**Parameters:**  
- `old`: The current password.  
- `new`: The new password to be set.

**Returns:**  
- `True` if the password is successfully updated.  
- `False` otherwise.

---

### `reset_password(password: str) -> bool`
**Warning:** This action will delete all device-to-device communication keys on the ESP.  
Use this only if you cannot remember the current password.

**Parameters:**  
- `password`: The reset password authorization string.

**Returns:**  
- `True` if the reset is successful.  
- `False` otherwise.

---

## Messaging

### `send_message(name: str, message: str) -> bool`
Sends a message to the ESP to be broadcasted.

**Parameters:**  
- `name`: The sender’s name or device identifier.  
- `message`: The message content to send.

**Returns:**  
- `True` if the message was sent successfully.  
- `False` otherwise.

---

### `receive_message() -> tuple[str, str]`
Receives messages from the ESP.

**Returns:**  
A tuple containing:
- `name`: The sender’s name or device identifier.  
- `message`: The message content received.

---

## Pairing

### `pair_devices() -> bool`
Initiates device pairing mode.

**Returns:**  
- `True` if pairing is successful.  
- `False` otherwise.

---

### `stop_pair() -> bool`
Cancels the ongoing pairing process.

**Returns:**  
- `True` if pairing was successfully stopped.  
- `False` otherwise.
