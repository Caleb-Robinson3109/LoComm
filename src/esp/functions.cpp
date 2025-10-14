#include "functions.h"

const char* Log(LOG_LEVEL level, const char* text) {
  if (level <= CURRENT_LOG_LEVEL) {
    return sprintf("[%s]: %s\n", logLevelEnumToChar(level), text);
  }
  return "";
}

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

