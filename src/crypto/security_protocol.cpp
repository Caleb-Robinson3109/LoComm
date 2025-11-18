#include "security_protocol.h"
#include "Preferences.h"
#include <string.h>
#include "mbedtls/sha256.h"
#include "mbedtls/pkcs5.h"
#include "mbedtls/gcm.h"
#include "mbedtls/aes.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/entropy.h"

#define NVM_NAMESPACE "LoComm"
#define NVM_KEY_SALT "sec_salt"
#define NVM_KEY_HASH "sec_hash"
#define NVM_KEY_D2D_KEY "sec_d2d_key"

// --- Global State ---
static Preferences storage;
static mbedtls_entropy_context entropy;
static mbedtls_ctr_drbg_context drbg;

static bool g_is_initialized = false;
static bool g_is_logged_in = false;
static bool g_is_paired = false;

// Persistent storage mirrors
static uint8_t g_password_hash[32];     
static uint8_t g_password_salt[16];     
static uint8_t g_encrypted_d2d_key[32]; // 16 byte key + 16 byte tag

// RAM-only Secrets
static uint8_t g_decrypted_d2d_key[16]; // The active communication key
static uint8_t g_wrapping_key[32];      // The key derived from password (KEK)

// --- Base85 Helpers (Z85 Standard) ---
static const char* Z85_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#";

// Helper to encode 4 bytes -> 5 chars
static void _z85_encode_block(const uint8_t* src, char* dest) {
    uint32_t val = (src[0] << 24) | (src[1] << 16) | (src[2] << 8) | src[3];
    for (int i = 4; i >= 0; i--) {
        dest[i] = Z85_CHARS[val % 85];
        val /= 85;
    }
}

// Helper to decode 5 chars -> 4 bytes
static bool _z85_decode_block(const char* src, uint8_t* dest) {
    uint32_t val = 0;
    for (int i = 0; i < 5; i++) {
        const char* found = strchr(Z85_CHARS, src[i]);
        if (!found) return false; // Invalid char
        val = val * 85 + (found - Z85_CHARS);
    }
    dest[0] = (val >> 24) & 0xFF;
    dest[1] = (val >> 16) & 0xFF;
    dest[2] = (val >> 8) & 0xFF;
    dest[3] = val & 0xFF;
    return true;
}

// --- Cryptographic Helpers ---

static bool _sec_generate_salt(uint8_t* saltBuffer, size_t saltLen) {
    if (!g_is_initialized) return false;
    return mbedtls_ctr_drbg_random(&drbg, saltBuffer, saltLen) == 0;
}

static bool _sec_hash_password(const char* password, const uint8_t* salt, uint8_t* outputHash) {
    mbedtls_sha256_context sha_ctx;
    mbedtls_sha256_init(&sha_ctx);
    if (mbedtls_sha256_starts(&sha_ctx, 0) != 0) { mbedtls_sha256_free(&sha_ctx); return false; }
    mbedtls_sha256_update(&sha_ctx, salt, 16);
    mbedtls_sha256_update(&sha_ctx, (const uint8_t*)password, strlen(password));
    int ret = mbedtls_sha256_finish(&sha_ctx, outputHash);
    mbedtls_sha256_free(&sha_ctx);
    return ret == 0;
}

static bool _sec_derive_key(const char* password, const uint8_t* salt, uint8_t* outputKey) {
    mbedtls_md_context_t sha_ctx;
    mbedtls_md_init(&sha_ctx);
    const mbedtls_md_info_t *info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
    if (mbedtls_md_setup(&sha_ctx, info, 1) != 0) { mbedtls_md_free(&sha_ctx); return false; }
    int ret = mbedtls_pkcs5_pbkdf2_hmac(&sha_ctx, (const unsigned char*)password, strlen(password), salt, 16, 10000, 32, outputKey);
    mbedtls_md_free(&sha_ctx);
    return ret == 0;
}

// ** NEW HELPER **
// Encrypts the current RAM D2D key using the RAM Wrapping key and saves to NVM
static bool _sec_encrypt_and_save_d2d_key() {
    mbedtls_gcm_context gcm;
    mbedtls_gcm_init(&gcm);
    
    // Setup GCM with the Wrapping Key (32 bytes / 256 bits)
    int ret = mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES, g_wrapping_key, 256);
    if (ret != 0) { mbedtls_gcm_free(&gcm); return false; }

    // Encrypt: g_decrypted_d2d_key (16) -> g_encrypted_d2d_key (32)
    // We use the first 12 bytes of the salt as the IV.
    ret = mbedtls_gcm_crypt_and_tag(&gcm, MBEDTLS_GCM_ENCRYPT, 16,
                                    g_password_salt, 12, // IV
                                    NULL, 0, 
                                    g_decrypted_d2d_key,
                                    g_encrypted_d2d_key,
                                    16, // Tag length
                                    g_encrypted_d2d_key + 16); // Tag goes after data

    mbedtls_gcm_free(&gcm);

    if (ret == 0) {
        storage.putBytes(NVM_KEY_D2D_KEY, g_encrypted_d2d_key, 32);
        g_is_paired = true;
        return true;
    }
    return false;
}


// --- Lifecycle ---

bool sec_init() {
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&drbg);
    const char* seed = "locomm_security_seed";
    mbedtls_ctr_drbg_seed(&drbg, mbedtls_entropy_func, &entropy, (const uint8_t*)seed, strlen(seed));
    
    g_is_initialized = true;
    if (!storage.begin(NVM_NAMESPACE, false)) { g_is_initialized = false; return false; }

    // Default Provisioning
    if (!storage.isKey(NVM_KEY_SALT)) {
        if (!sec_setInitialPassword("password")) { storage.end(); return false; }
    }

    // Load Data
    storage.getBytes(NVM_KEY_SALT, g_password_salt, 16);
    storage.getBytes(NVM_KEY_HASH, g_password_hash, 32);

    if (storage.isKey(NVM_KEY_D2D_KEY)) {
        storage.getBytes(NVM_KEY_D2D_KEY, g_encrypted_d2d_key, 32);
        g_is_paired = true;
    } else {
        memset(g_encrypted_d2d_key, 0, 32);
        g_is_paired = false;
    }

    // Clear RAM secrets
    sec_logout();
    return true;
}

void sec_deinit() {
    sec_logout(); // Wipes keys
    memset(g_password_hash, 0, 32);
    memset(g_password_salt, 0, 16);
    memset(g_encrypted_d2d_key, 0, 32);
    g_is_initialized = false;
    mbedtls_ctr_drbg_free(&drbg);
    mbedtls_entropy_free(&entropy);
    storage.end();
}


// --- Auth ---

bool sec_setInitialPassword(const char* password) {
    if (!g_is_initialized) return false;
    
    if (!_sec_generate_salt(g_password_salt, 16)) return false;
    if (!_sec_hash_password(password, g_password_salt, g_password_hash)) return false;

    storage.putBytes(NVM_KEY_SALT, g_password_salt, 16);
    storage.putBytes(NVM_KEY_HASH, g_password_hash, 32);
    
    sec_resetPairing(); // Reset pairing on new password setup
    return true;
}

bool sec_changePassword(const char* oldPassword, const char* newPassword) {
    if (!sec_login(oldPassword)) return false;

    // Optimization: If not paired, just set keys.
    if (!g_is_paired) {
        bool ret = sec_setInitialPassword(newPassword);
        sec_logout();
        return ret;
    }

    // 1. Generate New Salt & Hash
    if (!_sec_generate_salt(g_password_salt, 16)) { sec_logout(); return false; }
    if (!_sec_hash_password(newPassword, g_password_salt, g_password_hash)) { sec_logout(); return false; }
    
    // 2. Derive New Wrapping Key
    if (!_sec_derive_key(newPassword, g_password_salt, g_wrapping_key)) { sec_logout(); return false; }

    // 3. Encrypt the EXISTING D2D key with the NEW Wrapping Key
    // _sec_encrypt_and_save uses global g_wrapping_key and g_decrypted_d2d_key
    bool ret = _sec_encrypt_and_save_d2d_key();

    // 4. Update NVM for Salt/Hash (Key was updated in helper)
    storage.putBytes(NVM_KEY_SALT, g_password_salt, 16);
    storage.putBytes(NVM_KEY_HASH, g_password_hash, 32);

    sec_logout();
    return ret;
}

bool sec_login(const char* password) {
    if (!g_is_initialized) return false;

    // 1. Verify Hash
    uint8_t temp_hash[32];
    if (!_sec_hash_password(password, g_password_salt, temp_hash)) return false;
    if (memcmp(temp_hash, g_password_hash, 32) != 0) return false;

    // 2. Derive Wrapping Key (Store in RAM)
    if (!_sec_derive_key(password, g_password_salt, g_wrapping_key)) return false;

    // 3. If paired, Decrypt D2D Key
    if (g_is_paired) {
        mbedtls_gcm_context gcm;
        mbedtls_gcm_init(&gcm);
        int ret = mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES, g_wrapping_key, 256);
        if (ret == 0) {
            ret = mbedtls_gcm_auth_decrypt(&gcm, 16,
                                         g_password_salt, 12, // IV
                                         NULL, 0,
                                         g_encrypted_d2d_key + 16, 16, // Tag
                                         g_encrypted_d2d_key, // Ciphertext
                                         g_decrypted_d2d_key); // Output
        }
        mbedtls_gcm_free(&gcm);
        
        if (ret != 0) {
            // Decryption failed (corrupt data?)
            memset(g_wrapping_key, 0, 32);
            return false;
        }
    }

    g_is_logged_in = true;
    return true;
}

void sec_logout() {
    memset(g_decrypted_d2d_key, 0, 16);
    memset(g_wrapping_key, 0, 32); // Wipe the wrapping key
    g_is_logged_in = false;
}

bool sec_isLoggedIn() { return g_is_logged_in; }


// --- Manual Key Provisioning ---

bool sec_generate_key(char* outputBase85Buffer, size_t bufferSize) {
    if (!g_is_logged_in || bufferSize <= 20) return false;

    // 1. Generate Random D2D Key
    mbedtls_ctr_drbg_random(&drbg, g_decrypted_d2d_key, 16);

    // 2. Encode for display
    for (int i = 0; i < 4; i++) {
        _z85_encode_block(g_decrypted_d2d_key + (i*4), outputBase85Buffer + (i*5));
    }
    outputBase85Buffer[20] = '\0';

    // 3. Encrypt & Save (Using the wrapping key currently in RAM)
    return _sec_encrypt_and_save_d2d_key();
}

bool sec_log_key(const char* inputBase85String) {
    if (!g_is_logged_in || strlen(inputBase85String) != 20) return false;

    // 1. Decode String
    for (int i = 0; i < 4; i++) {
        if (!_z85_decode_block(inputBase85String + (i*5), g_decrypted_d2d_key + (i*4))) {
            memset(g_decrypted_d2d_key, 0, 16); // Clear on failure
            return false;
        }
    }

    // 2. Encrypt & Save
    return _sec_encrypt_and_save_d2d_key();
}

bool sec_display_key(char* outputBase85Buffer, size_t bufferSize) {
    if (!g_is_logged_in || !g_is_paired || bufferSize <= 20) return false;

    for (int i = 0; i < 4; i++) {
        _z85_encode_block(g_decrypted_d2d_key + (i*4), outputBase85Buffer + (i*5));
    }
    outputBase85Buffer[20] = '\0';
    return true;
}

bool sec_isPaired() { return g_is_paired; }

void sec_resetPairing() {
    storage.remove(NVM_KEY_D2D_KEY);
    memset(g_encrypted_d2d_key, 0, 32);
    memset(g_decrypted_d2d_key, 0, 16);
    g_is_paired = false;
}


// --- Encryption/Decryption ---

bool sec_encryptD2DMessage(const uint8_t* plaintext, size_t plaintextLen, uint8_t* ciphertextBuffer, size_t bufferSize, size_t* ciphertextLen) {
    if (!g_is_logged_in || !g_is_paired) return false;
    // CHANGED: Overhead reduced from 28 to 20 (12 IV + 8 Tag)
    if (bufferSize < plaintextLen + 20) return false;

    mbedtls_gcm_context gcm;
    mbedtls_gcm_init(&gcm);
    mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES, g_decrypted_d2d_key, 128); // 128-bit key

    uint8_t iv[12];
    mbedtls_ctr_drbg_random(&drbg, iv, 12); // Generate random IV

    // Output: [IV (12)] [Ciphertext (N)] [Tag (8)]
    int ret = mbedtls_gcm_crypt_and_tag(&gcm, MBEDTLS_GCM_ENCRYPT, plaintextLen,
                                        iv, 12, NULL, 0,
                                        plaintext, 
                                        ciphertextBuffer + 12, // Ciphertext starts after IV
                                        8, //Tag length is 8 bytes
                                        ciphertextBuffer + 12 + plaintextLen); // Tag starts after ciphertext

    // Copy IV to front
    memcpy(ciphertextBuffer, iv, 12);
    *ciphertextLen = 12 + plaintextLen + 8;

    mbedtls_gcm_free(&gcm);
    return (ret == 0);
}

bool sec_decryptD2DMessage(const uint8_t* ciphertext, size_t ciphertextLen, uint8_t* plaintextBuffer, size_t bufferSize, size_t* plaintextLen) {
    if (!g_is_logged_in || !g_is_paired) return false;
    
    if (ciphertextLen < 20) return false; 

    
    size_t dataLen = ciphertextLen - 20;
    if (bufferSize < dataLen) return false;

    mbedtls_gcm_context gcm;
    mbedtls_gcm_init(&gcm);
    mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES, g_decrypted_d2d_key, 128);

    int ret = mbedtls_gcm_auth_decrypt(&gcm, dataLen,
                                       ciphertext, 12, // IV at start
                                       NULL, 0,
                                       ciphertext + 12 + dataLen, 8, // Expect 8 byte Tag
                                       ciphertext + 12, // Ciphertext data
                                       plaintextBuffer);

    *plaintextLen = dataLen;
    mbedtls_gcm_free(&gcm);
    return (ret == 0);
}
