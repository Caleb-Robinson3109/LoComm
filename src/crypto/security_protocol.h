#ifndef SECURITY_PROTOCOL_H
#define SECURITY_PROTOCOL_H

#include <stdint.h>
#include <stddef.h>

// Use extern "C" to ensure C-linkage, making it compatible with C++ and C.
#ifdef __cplusplus
extern "C" {
#endif

// --- Lifecycle and Initialization ---

/**
 * @brief Initializes the security module.
 * Loads credentials from non-volatile storage and prepares the module for use.
 * Manages internal state, which must be stored in a .c/.cpp file.
 */
// CALL THIS UPON DEVICE SETUP 
bool sec_init();

/**
 * @brief Securely deinitializes the module.
 * Wipes any sensitive data (like decrypted keys) from RAM.
 */
// CALL THIS UPON DEVICE SHUTDOWN (USE esp_register_shutdown_handler())
void sec_deinit();


// --- Computer-to-Device: Password and Key Management ---

/**
 * @brief Sets the initial password during device provisioning.
 * This should be forced on the user during the first setup.
 */
// CALLED INSIDE OF sec_init() DOES NOT NEED TO BE CALLED EXTERNALLY
bool sec_setInitialPassword(const char* password);

/**
 * @brief Changes the user's password.
 * Decrypts the stored D2D key with the old password and re-encrypts it with the new one
 * Replaces hashed password.
 */
// CALL THIS, NOT sec_setInitialPassword. DEFAULT PASSWORD IS "password"
bool sec_changePassword(const char* oldPassword, const char* newPassword);

/**
 * @brief Verifies a password and prepares for a secure session.
 * If correct, it derives the master key and decrypts the D2D key into RAM.
 */
// CALL THiS DURING LOGIN PROCESS
bool sec_login(const char* password);

/**
 * @brief Ends the computer-to-device session.
 * Flushes the password and the decrypted D2D key from memory for security.
 */
// CALL THIS UPON LOGOUT (if that's a thing we are doing)
void sec_logout();

/**
 * @brief Checks if a user is currently logged in.
 * Returns true if a valid password has been entered and not yet flushed by logout().
 */
// General use
bool sec_isLoggedIn();


// --- Device-to-Device: Pairing Sequence --- NOTE: WILL BE CHANGED

/**
 * @brief Begins the pairing sequence by generating a new key pair.
 * Provides the public key to be sent to the other device.
 */
bool sec_startPairing(uint8_t* publicKeyBuffer, size_t bufferSize, size_t* publicKeyLen);

/**
 * @brief Completes the pairing sequence using the other device's public key.
 * Computes the shared secret and establishes the symmetric key for the D2D session.
 */
bool sec_finalizePairing(const uint8_t* theirPublicKey, size_t theirKeyLen);

/**
 * @brief Checks if a secure D2D channel has been established.
 * Returns true if a shared symmetric key exists from a successful pairing.
 */
bool sec_isPaired();

/**
 * @brief Resets the pairing state.
 * Deletes the shared symmetric D2D key, requiring a new pairing sequence.
 */
void sec_resetPairing();


// --- Device-to-Device: Secure Data Transmission ---

/**
 * @brief Encrypts and authenticates a message using the shared D2D key.
 * Uses an AEAD cipher like AES-GCM to provide confidentiality and integrity.
 */
bool sec_encryptD2DMessage(const uint8_t* plaintext, size_t plaintextLen, uint8_t* ciphertextBuffer, size_t bufferSize, size_t* ciphertextLen);

/**
 * @brief Decrypts and verifies an incoming message using the shared D2D key.
 * Will fail if the message has been tampered with or is not from the paired device.
 */
bool sec_decryptD2DMessage(const uint8_t* ciphertext, size_t ciphertextLen, uint8_t* plaintextBuffer, size_t bufferSize, size_t* plaintextLen);


#ifdef __cplusplus
}
#endif

#endif // SECURITY_PROTOCOL_H
