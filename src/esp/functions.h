#pragma once

#define CURRENT_LOG_LEVEL LOG_LEVEL_DEBUG

#include <stdio.h>
#include "CyclicArrayList.h"

enum LOG_LEVEL { LOG_LEVEL_ERROR, LOG_LEVEL_WARNING, LOG_LEVEL_LOG, LOG_LEVEL_DEBUG };

void Log(LOG_LEVEL level, const char* text);
const char* logLevelEnumToChar(LOG_LEVEL level);