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
// CALLED INSIDE OF sec_init() OR can be called externally if needed. It is probably not needed.
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


// --- Device-to-Device: Manual Key Provisioning ---

/**
 * @brief Generates a new D2D key and encodes it for display.
 * This is for the "master" device. The user must be logged in.
 * The new key is stored, and the Base85 string is returned to be shown on-screen.
 * @param outputBase85Buffer An empty buffer to write the Base85 string into.
 * @param bufferSize The size of the outputBase85Buffer (must be > 20).
 * @return true on success, false on failure (not logged in, etc.).
 */
bool sec_generate_key(char* outputBase85Buffer, size_t bufferSize);

/**
 * @brief Provisions the D2D key from a manually entered string.
 * This is for the "member" device. The user must be logged in.
 * The string is decoded, and the resulting key is stored.
 * @param inputBase85String The 20-character Base85 string entered by the user.
 * @return true on success, false on failure (not logged in, invalid string, etc.).
 */
bool sec_log_key(const char* inputBase85String);


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
//plaintext: Pointer to the data you want to encrypt
//plaintextLen: Length of the data you want to encrypt
//ciphertextBuffer: Where you want the encrypted message to be stored
//bufferSize: maximum size of the buffer (to prevent overflow)
//ciphertextLen: the size of the ciphertext
/* * * * * * * * * * * * * * * * *    EXAMPLE USAGE    * * * * * * * * * * * * * * *   
// Your message to send
const char* message = "This is a secret message.";
size_t messageLen = strlen(message); // Length is 25

// --- 1. Prepare Buffers ---

// Define a buffer for the output. This is to prevent memory leakage.
// We know it needs to be at least 25 + 28 = 53 bytes.
// We'll make it 100 to be safe. You could also just make it messageLen + encryption_overhead
uint8_t encryptedBuffer[100];
size_t maxBufferSize = 100;

// This variable will hold the *actual* final size
size_t actualEncryptedLen = 0; 

// --- 2. Call the Function ---
bool success = sec_encryptD2DMessage(
    (const uint8_t*)message, // The data to encrypt
    messageLen,              // The length of that data
    encryptedBuffer,         // The empty buffer for the result
    maxBufferSize,           // The *max* size of our empty buffer (for safety!)
    &actualEncryptedLen      // A pointer to our length variable
);

// --- 3. Check the Result ---
if (success) {
    // It worked!
    // 'encryptedBuffer' now contains the encrypted data.
    // 'actualEncryptedLen' is now 53 (25 + 28).
    // You can now send 'actualEncryptedLen' bytes from 'encryptedBuffer'.
    //
    // e.g., lora_send(encryptedBuffer, actualEncryptedLen);

} else {
    // Encryption failed.
    // This could be because you're not logged in, or some other error.
}
*/
bool sec_encryptD2DMessage(const uint8_t* plaintext, size_t plaintextLen, uint8_t* ciphertextBuffer, size_t bufferSize, size_t* ciphertextLen);

/**
 * @brief Decrypts and verifies an incoming message using the shared D2D key.
 * Will fail if the message has been tampered with or is not from the paired device.
 */
// Example usage is nearly the same as above, except bufferSize should be ciphertextLen - encryption_overhead
bool sec_decryptD2DMessage(const uint8_t* ciphertext, size_t ciphertextLen, uint8_t* plaintextBuffer, size_t bufferSize, size_t* plaintextLen);


#ifdef __cplusplus
}
#endif

#endif // SECURITY_PROTOCOL_H
