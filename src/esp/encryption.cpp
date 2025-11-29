// do not use


// implement keygen stuff here
#include "mbedtls/sha256.h"
#include "mbedtls/pkcs5.h"      // Note: PBKDF2 is within pkcs5.h
#include "mbedtls/ecdh.h"
#include "mbedtls/ecp.h"
#include "mbedtls/gcm.h"
#include "mbedtls/aes.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/entropy.h"    


#include <stdint.h>
#include <stddef.h>

class SecurityProtocol {
public:
    SecurityProtocol();
    ~SecurityProtocol();

    // --- Lifecycle and Initialization ---

    /**
     * @brief Initializes the security module.
     * Loads credentials from non-volatile storage and prepares the module for use.
     */
    bool init();

    /**
     * @brief Securely deinitializes the module.
     * Wipes any sensitive data (like decrypted keys) from RAM.
     */
    void deinit();


    // --- Computer-to-Device: Password and Key Management ---

    /**
     * @brief Sets the initial password during device provisioning.
     * This should be forced on the user during the first setup.
     */
    bool setInitialPassword(const char* password);

    /**
     * @brief Changes the user's password.
     * Decrypts the stored D2D key with the old password and re-encrypts it with the new one.
     */
    bool changePassword(const char* oldPassword, const char* newPassword);

    /**
     * @brief Verifies a password and prepares for a secure session.
     * If correct, it derives the master key and decrypts the D2D key into RAM.
     */
    bool login(const char* password);

    /**
     * @brief Ends the computer-to-device session.
     * Flushes the password and the decrypted D2D key from memory for security.
     */
    void logout();
    
    /**
     * @brief Checks if a user is currently logged in.
     * Returns true if a valid password has been entered and not yet flushed by logout().
     */
    bool isLoggedIn() const;


    // --- Device-to-Device: Pairing Sequence ---
    
    /**
     * @brief Begins the pairing sequence by generating a new key pair.
     * Provides the public key to be sent to the other device.
     */
    bool startPairing(uint8_t* publicKeyBuffer, size_t bufferSize, size_t* publicKeyLen);
        // use mbedtls_ecdh here
    /**
     * @brief Completes the pairing sequence using the other device's public key.
     * Computes the shared secret and establishes the symmetric key for the D2D session.
     */
    bool finalizePairing(const uint8_t* theirPublicKey, size_t theirKeyLen);
        // use mbedtls_ecp here
    /**
     * @brief Checks if a secure D2D channel has been established.
     * Returns true if a shared symmetric key exists from a successful pairing.
     */
    bool isPaired() const;
    
    /**
     * @brief Resets the pairing state.
     * Deletes the shared symmetric D2D key, requiring a new pairing sequence.
     */
    void resetPairing();


    // --- Device-to-Device: Secure Data Transmission ---

    /**
     * @brief Encrypts and authenticates a message using the shared D2D key.
     * Uses an AEAD cipher like AES-GCM to provide confidentiality and integrity.
     */
    bool encryptD2DMessage(const uint8_t* plaintext, size_t plaintextLen, uint8_t* ciphertextBuffer, size_t bufferSize, size_t* ciphertextLen);
        // use mbedtls_gcm here (encryption)
    /**
     * @brief Decrypts and verifies an incoming message using the shared D2D key.
     * Will fail if the message has been tampered with or is not from the paired device.
     */
    bool decryptD2DMessage(const uint8_t* ciphertext, size_t ciphertextLen, uint8_t* plaintextBuffer, size_t bufferSize, size_t* plaintextLen);
        //use mbedtls_gcm here (decryption)

private:
    // --- Internal State (Variables would go here) ---
    // e.g., bool loggedIn;
    // e.g., uint8_t deviceToDeviceKey[32];

    
    // --- Internal Helper Functions ---

    /**
     * @brief Derives a strong cryptographic key from a user-provided password.
     * Uses a KDF like PBKDF2 with a stored salt.
     */
    bool _deriveKeyFromPassword(const char* password, const uint8_t* salt, uint8_t* outputKey);
        // use mbedtls_pkcs5_pbkdf2_hmac here
    /**
     * @brief Creates a salted hash of a password for secure storage.
     * Uses a standard hashing algorithm like SHA-256.
     */
    void _hashPassword(const char* password, uint8_t* salt, uint8_t* outputHash);
        // use mbedtls_sha256 here
    /**
     * @brief Loads the salt, password hash, and encrypted D2D key from NVS.
     * This is called during the init() sequence.
     */
    bool _loadCredentials();

    /**
     * @brief Saves the current salt, password hash, and encrypted D2D key to NVS.
     * This is called when the password is changed or a key is established.
     */
    bool _saveCredentials();
};
