#ifndef SECURITY_PROTOCOL_H
#define SECURITY_PROTOCOL_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// --- Lifecycle and Initialization ---

/**
 * @brief Initializes the security module.
 * MUST be called once at startup before any other function.
 * * This function:
 * 1. Initializes the hardware random number generator (RNG).
 * 2. Opens the Non-Volatile Memory (NVM) namespace "LoComm".
 * 3. Loads encrypted keys and password hashes from NVM into RAM.
 * 4. Sets the initial state to logged out.
 * * @return true if initialization and loading were successful.
 * @return false if NVM could not be accessed or RNG failed.
 */
bool sec_init();

/**
 * @brief Securely wipes secrets and shuts down the module.
 * Should be called before system shutdown or restart.
 * * This function securely clears (memset to 0) all sensitive keys 
 * (decrypted D2D keys, wrapping keys) from RAM.
 */
void sec_deinit();


// --- Computer-to-Device: Password and Key Management ---

/**
 * @brief Sets the initial password during device provisioning.
 * This will overwrite any existing password and wipe any existing pairing keys.
 * * @param password A null-terminated C-string.
 * @return true on success, false if the module is not initialized.
 */
bool sec_setInitialPassword(const char* password);

/**
 * @brief Changes the user's password and re-encrypts the D2D key.
 * * Flow:
 * 1. Verifies oldPassword.
 * 2. If a D2D key exists, decrypts it using the old password.
 * 3. Generates a new salt and derives a new wrapping key from newPassword.
 * 4. Re-encrypts the D2D key with the new wrapping key and saves to NVM.
 * * @param oldPassword Current password (null-terminated string).
 * @param newPassword New password (null-terminated string).
 * @return true if change was successful.
 * @return false if oldPassword was wrong or NVM write failed.
 */
bool sec_changePassword(const char* oldPassword, const char* newPassword);

/**
 * @brief Logs the user in, unlocking the secure D2D key.
 * * This function derives the wrapping key from the password and uses it 
 * to decrypt the D2D key stored in NVM. The decrypted key is held in 
 * RAM until sec_logout() is called.
 * * @param password The user's password (null-terminated string).
 * @return true if password matches and key decryption succeeds.
 */
bool sec_login(const char* password);

/**
 * @brief Logs the user out and wipes secrets from RAM.
 * * Immediately overwrites the decrypted D2D key and wrapping key 
 * in memory with zeros.
 */
void sec_logout();

/**
 * @brief Checks if the secure D2D key is currently available in RAM.
 * @return true if logged in, false otherwise.
 */
bool sec_isLoggedIn();


// --- Device-to-Device: Manual Key Provisioning ---

/**
 * @brief Generates a NEW D2D key and provides a display string.
 * * Call this on the "Master" device during pairing.
 * 1. Generates a random 128-bit key.
 * 2. Encrypts and saves it to NVM (using the current user's password).
 * 3. Encodes the key into a 20-character Base85 string for the UI.
 * * @param outputBase85Buffer Pointer to a buffer allocated by the caller.
 * @param bufferSize Size of the buffer. MUST be >= 21 bytes (20 chars + null terminator).
 * @return true on success, false if not logged in or buffer too small.
 */
bool sec_generate_key(char* outputBase85Buffer, size_t bufferSize);

/**
 * @brief Inputs a pairing string to set the D2D key.
 * * Call this on the "Member" device.
 * 1. Decodes the 20-character string into a 128-bit key.
 * 2. Encrypts and saves it to NVM (using the current user's password).
 * * @param inputBase85String A null-terminated string of exactly 20 Base85 characters.
 * @return true on success, false if string is invalid or user not logged in.
 */
bool sec_log_key(const char* inputBase85String);

/**
 * @brief Re-exports the EXISTING D2D key for display.
 * * Use this to add a third member to an existing group.
 * The device must already be paired and logged in.
 * * @param outputBase85Buffer Pointer to a buffer allocated by the caller.
 * @param bufferSize Size of the buffer. MUST be >= 21 bytes.
 * @return true on success, false if not paired or not logged in.
 */
bool sec_display_key(char* outputBase85Buffer, size_t bufferSize);

/**
 * @brief Checks if a D2D key is stored in NVM.
 * @return true if the device has been paired, false otherwise.
 */
bool sec_isPaired();

/**
 * @brief Deletes the D2D key from NVM and RAM.
 * Requires the user to re-pair to communicate again.
 */
void sec_resetPairing();


// --- Device-to-Device: Secure Data Transmission ---

/**
 * @brief Encrypts a message using AES-GCM.
 * Adds a 12-byte IV and a 16-byte Authentication Tag.
 * * Overhead: The output will be exactly (plaintextLen + 28) bytes.
 * Format: [IV (12 bytes)] [Ciphertext (N bytes)] [Auth Tag (16 bytes)]
 * * @param plaintext Source data to encrypt.
 * @param plaintextLen Length of the source data.
 * @param ciphertextBuffer Dest buffer allocated by caller.
 * @param bufferSize Size of dest buffer. MUST be >= (plaintextLen + 28).
 * @param ciphertextLen Output pointer. Function writes the final size here (plaintextLen + 28).
 * @return true on success, false if buffer too small or not logged in.
 */
bool sec_encryptD2DMessage(const uint8_t* plaintext, size_t plaintextLen, uint8_t* ciphertextBuffer, size_t bufferSize, size_t* ciphertextLen);

/**
 * @brief Decrypts and Authenticates a message using AES-GCM.
 * * Performs an integrity check using the Auth Tag. If the message has 
 * been tampered with, this function will return false and produce no output.
 * * @param ciphertext Source encrypted data (IV + Ciphertext + Tag).
 * @param ciphertextLen Total length of encrypted data.
 * @param plaintextBuffer Dest buffer allocated by caller.
 * @param bufferSize Size of dest buffer. MUST be >= (ciphertextLen - 28).
 * @param plaintextLen Output pointer. Function writes final decrypted size here.
 * @return true if integrity check passed and decryption succeeded.
 * @return false if authentication failed (tampering) or buffer too small.
 */
bool sec_decryptD2DMessage(const uint8_t* ciphertext, size_t ciphertextLen, uint8_t* plaintextBuffer, size_t bufferSize, size_t* plaintextLen);

#ifdef __cplusplus
}
#endif

#endif // SECURITY_PROTOCOL_H
