#include "security_protocol.h"

// --- ESP32 & NVM Includes ---
#include "Preferences.h" // ESP32 NVM storage library
#include <string.h>      // For memset, memcpy

// --- Mbed TLS Includes ---
#include "mbedtls/sha256.h"
#include "mbedtls/pkcs5.h"      // For PBKDF2
#include "mbedtls/gcm.h"
#include "mbedtls/aes.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/entropy.h"

// --- NVM Key Constants ---
// These are the "keys" for the key-value store in NVM
#define NVM_NAMESPACE "LoComm"
#define NVM_KEY_SALT "sec_salt"
#define NVM_KEY_HASH "sec_hash"
#define NVM_KEY_D2D_KEY "sec_d2d_key"

// --- Internal State Variables (Module-Private) ---

// NVM Storage Handle
static Preferences storage;

// mbedTLS Cryptographic Contexts
static mbedtls_entropy_context entropy;
static mbedtls_ctr_drbg_context drbg;

// State Flags
static bool g_is_initialized = false;
static bool g_is_logged_in = false;
static bool g_is_paired = false; // Note: 'is_paired' will be true if a D2D key exists

// NVM-backed data (loaded into RAM at init)
static uint8_t g_password_hash[32];     // The SHA-256 hash of the password
static uint8_t g_password_salt[16];     // 16-byte salt for hashing
static uint8_t g_encrypted_d2d_key[48]; // 32-byte key + 16-byte GCM tag

// The "golden" key. This is the most sensitive data.
// It ONLY exists in RAM and ONLY when logged in.
static uint8_t g_decrypted_d2d_key[32];

// --- Internal Helper Functions ---

/**
 * @brief Generates a cryptographically secure random salt.
 */
static bool _sec_generate_salt(uint8_t* saltBuffer, size_t saltLen) {
    if (!g_is_initialized) return false; // Ensure DRBG is ready
    return mbedtls_ctr_drbg_random(&drbg, saltBuffer, saltLen) == 0;
}

/**
 * @brief Hashes a password with a given salt using SHA-256.
 * (Note: This is for verification. PBKDF2 will be used for key derivation).
 */
static bool _sec_hash_password(const char* password, const uint8_t* salt, uint8_t* outputHash) {
    if (!password || !salt || !outputHash) return false;

    mbedtls_sha256_context sha_ctx;
    mbedtls_sha256_init(&sha_ctx);

    // Start SHA-256 in 256-bit mode
    if (mbedtls_sha256_starts(&sha_ctx, 0) != 0) {
        mbedtls_sha256_free(&sha_ctx);
        return false;
    }

    // Hash the salt first
    mbedtls_sha256_update(&sha_ctx, salt, 16);
    // Then hash the password
    mbedtls_sha256_update(&sha_ctx, (const uint8_t*)password, strlen(password));

    // Get the final hash
    if (mbedtls_sha256_finish(&sha_ctx, outputHash) != 0) {
        mbedtls_sha256_free(&sha_ctx);
        return false;
    }

    mbedtls_sha256_free(&sha_ctx);
    return true;
}

// --- Lifecycle and Initialization ---

bool sec_init() {
    // 1. Initialize mbedTLS Random Number Generator
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&drbg);

    // Seed the DRBG
    const char* seed = "locomm_security_seed";
    if (mbedtls_ctr_drbg_seed(&drbg, mbedtls_entropy_func, &entropy, (const uint8_t*)seed, strlen(seed)) != 0) {
        // Failed to seed DRBG, this is a critical failure
        return false;
    }
    g_is_initialized = true;

    // 2. Initialize NVM Storage
    if (!storage.begin(NVM_NAMESPACE, false)) { // false = Read/Write mode
        // Failed to open storage
        g_is_initialized = false;
        return false;
    }

    // 3. Check if device is provisioned (i.e., has a password salt)
    if (!storage.isKey(NVM_KEY_SALT)) {
        // Not provisioned. Set a default password.
        // This is the fixed version of your teammate's 'init_password'
        if (!sec_setInitialPassword("password")) {
            // Failed to set default password, critical failure
            storage.end();
            g_is_initialized = false;
            return false;
        }
    }

    // 4. Load credentials from NVM into RAM
    // We are now guaranteed that these keys exist (from check above)
    storage.getBytes(NVM_KEY_SALT, g_password_salt, 16);
    storage.getBytes(NVM_KEY_HASH, g_password_hash, 32);

    // 5. Load the D2D key if it exists.
    if (storage.isKey(NVM_KEY_D2D_KEY)) {
        storage.getBytes(NVM_KEY_D2D_KEY, g_encrypted_d2d_key, 48);
        g_is_paired = true; // We have a key, so we are "paired"
    } else {
        // No D2D key exists yet
        memset(g_encrypted_d2d_key, 0, 48); // Clear the buffer
        g_is_paired = false;
    }

    // 6. Finalize state
    g_is_logged_in = false;                // ALWAYS start in logged-out state
    memset(g_decrypted_d2d_key, 0, 32); // Securely wipe the target RAM
    
    // We don't close storage with storage.end() here, 
    // as we'll need it for other functions.

    return true;
}

void sec_deinit() {
    // Securely wipe all sensitive data from RAM
    memset(g_decrypted_d2d_key, 0, 32);
    memset(g_password_hash, 0, 32);
    memset(g_password_salt, 0, 16);
    memset(g_encrypted_d2d_key, 0, 48);

    g_is_logged_in = false;
    g_is_paired = false;
    g_is_initialized = false;

    // Free mbedTLS contexts
    mbedtls_ctr_drbg_free(&drbg);
    mbedtls_entropy_free(&entropy);

    // Close NVM storage
    storage.end();
}


// --- Computer-to-Device: Password and Key Management ---

bool sec_setInitialPassword(const char* password) {
    if (!g_is_initialized) return false; // Must call sec_init() first

    // 1. Generate a new random salt
    if (!_sec_generate_salt(g_password_salt, 16)) {
        return false; // Failed to get random numbers
    }

    // 2. Hash the password with the new salt
    if (!_sec_hash_password(password, g_password_salt, g_password_hash)) {
        return false; // Hashing failed
    }

    // 3. Save the new salt and hash to NVM
    storage.putBytes(NVM_KEY_SALT, g_password_salt, 16);
    storage.putBytes(NVM_KEY_HASH, g_password_hash, 32);
    
    // 4. If a D2D key exists, it is now orphaned. Delete it.
    // The user must re-pair after a password reset.
    if (storage.isKey(NVM_KEY_D2D_KEY)) {
        storage.remove(NVM_KEY_D2D_KEY);
        memset(g_encrypted_d2d_key, 0, 48);
        memset(g_decrypted_d2d_key, 0, 32);
        g_is_paired = false;
    }

    return true;
}

bool sec_changePassword(const char* oldPassword, const char* newPassword) {
    // STUB: To be implemented
    // 1. Call sec_login(oldPassword)
    // 2. If successful, g_decrypted_d2d_key is in RAM.
    // 3. Generate new salt, hash newPassword.
    // 4. Re-encrypt g_decrypted_d2d_key with new password.
    // 5. Save new salt, new hash, new encrypted key to NVM.
    // 6. sec_logout() to clear old state.
    return false;
}

bool sec_login(const char* password) {
    // STUB: To be implemented
    // 1. Hash the provided password with g_password_salt.
    // 2. Compare the result with g_password_hash (use a secure compare).
    // 3. If no match, return false.
    // 4. If match, derive PBKDF2 key from password.
    // 5. Use PBKDF2 key to decrypt g_encrypted_d2d_key into g_decrypted_d2d_key.
    // 6. If decryption succeeds, set g_is_logged_in = true and return true.
    return false;
}

void sec_logout() {
    // STUB: To be implemented
    // 1. memset(g_decrypted_d2d_key, 0, 32);
    // 2. g_is_logged_in = false;
}

bool sec_isLoggedIn() {
    // STUB: To be implemented
    return g_is_logged_in;
}


// --- Device-to-Device: Pairing Sequence ---

bool sec_startPairing(uint8_t* publicKeyBuffer, size_t bufferSize, size_t* publicKeyLen) {
    // STUB: To be implemented
    // 1. Check if logged in (g_is_logged_in == true).
    // 2. Use mbedtls_ecdh_gen_public to generate keys.
    return false;
}

bool sec_finalizePairing(const uint8_t* theirPublicKey, size_t theirKeyLen) {
    // STUB: To be implemented
    // 1. Check if logged in.
    // 2. Use mbedtls_ecdh_calc_secret to get shared secret.
    // 3. KDF the secret into g_decrypted_d2d_key.
    // 4. Encrypt g_decrypted_d2d_key using password-derived key.
    // 5. Store result in g_encrypted_d2d_key and save to NVM.
    // 6. Set g_is_paired = true.
    return false;
}

bool sec_isPaired() {
    // STUB: To be implemented
    return g_is_paired;
}

void sec_resetPairing() {
    // STUB: To be implemented
    // 1. storage.remove(NVM_KEY_D2D_KEY);
    // 2. memset(g_encrypted_d2d_key, 0, 48);
    // 3. memset(g_decrypted_d2d_key, 0, 32);
    // 4. g_is_paired = false;
}


// --- Device-to-Device: Secure Data Transmission ---

bool sec_encryptD2DMessage(const uint8_t* plaintext, size_t plaintextLen, uint8_t* ciphertextBuffer, size_t bufferSize, size_t* ciphertextLen) {
    // STUB: To be implemented
    // 1. Check if g_is_logged_in == true (so g_decrypted_d2d_key is available).
    // 2. Use mbedtls_gcm_encrypt with g_decrypted_d2d_key.
    return false;
}

bool sec_decryptD2DMessage(const uint8_t* ciphertext, size_t ciphertextLen, uint8_t* plaintextBuffer, size_t bufferSize, size_t* plaintextLen) {
    // STUB: To be implemented
    // 1. Check if g_is_logged_in == true.
    // 2. Use mbedtls_gcm_decrypt with g_decrypted_d2d_key.
    return false;
}
