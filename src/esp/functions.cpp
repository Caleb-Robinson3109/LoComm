#include "functions.h"

const char* logLevelEnumToChar(LOG_LEVEL level) {
  switch (level) {
    case LOG_LEVEL_ERROR:
      return "ERROR";
    case LOG_LEVEL_WARNING:
      return "WARNING";
    case LOG_LEVEL_LOG:
      return "LOG";
    case LOG_LEVEL_DEBUG:
      return "DEBUG";
    default:
      return "UNEXPECTED";
  }
}

void dumpArray16ToSerial(const uint16_t* src, const uint16_t size) {
  Serial1.printf("Dumping Array to Serial: \n");
  for (int i = 0; i < size; i++) {
    Serial1.printf("%d ", src[i]);
  }
  Serial1.printf("\n");
}

void runTests() { //TODO write unit tests for the arrays types
  delay(2000);
  
  DefraggingBuffer<2048, 8> testBuffer = DefraggingBuffer<2048, 8>();
  testBuffer.init();
  LLog("Defragging Buffer Tests:");
  LLog("Allocating a buffer of size 100");

  uint16_t bufferOneLocation = testBuffer.malloc(100); 
  if (bufferOneLocation != 0xFFFF) {
    LDebug("Successfully malloced a single buffer of size 100");
  } else {
    LError("Failed to malloc a single buffer of size 100");
    HALT();
  }
  Serial1.printf("numAllocations: %d\n", testBuffer.numAllocations);
  LLog("allocationStartPositions:");
  dumpArray16ToSerial(&(testBuffer.allocationStartPositions[0]), testBuffer.numAllocations);
  LLog("allocationSizes:");
  dumpArray16ToSerial(&(testBuffer.allocationSizes[0]), testBuffer.numAllocations);
  LLog("openSpaceBetweenAllocations:");
  dumpArray16ToSerial(&(testBuffer.openSpaceBetweenAllocations[0]), testBuffer.numAllocations + 1);

  LLog("Allocating a second buffer of size 70");
  if (testBuffer.malloc(70) != 0xFFFFFFFF) {
    LDebug("Successfully malloced a single buffer of size 70");
  } else {
    LError("Failed to malloc a second buffer of size 70");
    HALT();
  }

  Serial1.printf("numAllocations: %d\n", testBuffer.numAllocations);
  LLog("allocationStartPositions:");
  dumpArray16ToSerial(&(testBuffer.allocationStartPositions[0]), testBuffer.numAllocations);
  LLog("allocationSizes:");
  dumpArray16ToSerial(&(testBuffer.allocationSizes[0]), testBuffer.numAllocations);
  LLog("openSpaceBetweenAllocations:");
  dumpArray16ToSerial(&(testBuffer.openSpaceBetweenAllocations[0]), testBuffer.numAllocations + 1);

  LLog("Freeing the initial malloc:");
  if (testBuffer.free(0)) {
    LDebug("Successfully freed initial malloc");
  } else {
    LError("Failed to release initial malloc");
    HALT();
  }

  Serial1.printf("numAllocations: %d\n", testBuffer.numAllocations);
  LLog("allocationStartPositions:");
  dumpArray16ToSerial(&(testBuffer.allocationStartPositions[0]), testBuffer.numAllocations);
  LLog("allocationSizes:");
  dumpArray16ToSerial(&(testBuffer.allocationSizes[0]), testBuffer.numAllocations);
  LLog("openSpaceBetweenAllocations:");
  dumpArray16ToSerial(&(testBuffer.openSpaceBetweenAllocations[0]), testBuffer.numAllocations + 1); 

  uint32_t buffer3 = testBuffer.malloc(30);
  LLog("Mallocing a buffer of size 30, expecting it to be placted at the beginning");
  if (buffer3 != 0) {
    LError("Buffer was not placed at correct location!");
    HALT();
  }

  Serial1.printf("numAllocations: %d\n", testBuffer.numAllocations);
  LLog("allocationStartPositions:");
  dumpArray16ToSerial(&(testBuffer.allocationStartPositions[0]), testBuffer.numAllocations);
  LLog("allocationSizes:");
  dumpArray16ToSerial(&(testBuffer.allocationSizes[0]), testBuffer.numAllocations);
  LLog("openSpaceBetweenAllocations:");
  dumpArray16ToSerial(&(testBuffer.openSpaceBetweenAllocations[0]), testBuffer.numAllocations + 1); 

  LLog("Removing buffer that was just created");
  if (!testBuffer.free(0)) {
    LError("Failed to free buffer");
    HALT();
  }

  Serial1.printf("numAllocations: %d\n", testBuffer.numAllocations);
  LLog("allocationStartPositions:");
  dumpArray16ToSerial(&(testBuffer.allocationStartPositions[0]), testBuffer.numAllocations);
  LLog("allocationSizes:");
  dumpArray16ToSerial(&(testBuffer.allocationSizes[0]), testBuffer.numAllocations);
  LLog("openSpaceBetweenAllocations:");
  dumpArray16ToSerial(&(testBuffer.openSpaceBetweenAllocations[0]), testBuffer.numAllocations + 1); 

  //LLog("Deallocating")
  LLog("Passed all tests, exiting");
  HALT();
}

//This is a temporary implementation. All this will do is assert the buffer is big enough, copy over the plain text, and then add random data as the cipher overhead
bool encryptD2DMessage(const uint8_t* plaintext, size_t plaintextLen, uint8_t* ciphertextBuffer, size_t bufferSize, size_t* ciphertextLen) {
  return sec_encryptD2DMessage(plaintext, plaintextLen, ciphertextBuffer, bufferSize, ciphertextLen);
  //the outputsize will just be the plaintext size plus the overhead
  //if (bufferSize < plaintextLen + AES_GCM_OVERHEAD) return false;
  //memcpy(ciphertextBuffer, plaintext, plaintextLen);
  //esp_fill_random(ciphertextBuffer + plaintextLen, AES_GCM_OVERHEAD);
  //*ciphertextLen = plaintextLen + AES_GCM_OVERHEAD;
  //return true;
}

//This is a temporary implementation. All this will do is assert the buffer is big enough and copy over the plain text excluding the overhead
bool decryptD2DMessage(const uint8_t* ciphertext, size_t ciphertextLen, uint8_t* plaintextBuffer, size_t bufferSize, size_t* plaintextLen) {
  return sec_decryptD2DMessage(ciphertext, ciphertextLen, plaintextBuffer, bufferSize, plaintextLen);
  //if (ciphertextLen - AES_GCM_OVERHEAD < 1) return false;
  //if (ciphertextLen - AES_GCM_OVERHEAD > bufferSize) return false;
  //memcpy(plaintextBuffer, ciphertext, ciphertextLen - AES_GCM_OVERHEAD);
  //*plaintextLen = ciphertextLen - AES_GCM_OVERHEAD;
  //return true;
}
