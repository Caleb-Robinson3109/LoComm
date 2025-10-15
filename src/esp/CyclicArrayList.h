#pragma once

//TODO this could be optimized by actually tracking size instead of calculating it

template <int SIZE>
class CyclicArrayList {
  public:
    //CyclicArrayList();

    const uint8_t& operator[](unsigned int index) {
      if (index >= SIZE) {
        return buffer[0]; //TODO this is not ideal, but there is no error handling
      } else {
        index += bufferStart;
        if (index >= SIZE) index -= SIZE;
        return buffer[index];
      }
    }

    uint32_t spaceLeft() {
      if (bufferFull) return 0;
      if (bufferStart == bufferEnd) {
        return SIZE;
      }
      if (bufferStart < bufferEnd) {
        return bufferStart + (SIZE - bufferEnd);
      }
      return bufferStart - bufferEnd;
    }

    uint32_t size() {
      return SIZE - this->spaceLeft();
    }

    bool pushBack(uint8_t* src, int size) {
      if (size > this->spaceLeft()) return false;
      
      if (SIZE - bufferEnd < size) { //If adding to the buffer would wrap it around...
        memcpy(&(buffer[bufferEnd]), src, sizeof(uint8_t) * (SIZE - bufferEnd));
        memcpy(buffer, src, sizeof(uint8_t) * (size - (SIZE - bufferEnd)));
        bufferEnd = (size - (SIZE - bufferEnd));
      } else { 
        memcpy(&(buffer[bufferEnd]), src, sizeof(uint8_t) * (size));
        bufferEnd += size;
      }
      return true;
    }

    bool peakFront(uint8_t* dst, int size) {
      return true;
    }

    bool dropFront(int size) {
      if (size == 0) return true;
      if (size >= this->size()) {
        bufferStart = 0;
        bufferEnd = 0;
      } else {
        bufferStart += size;
        if (bufferStart >= SIZE) bufferStart -= SIZE;
      }
      return true;
    }

  private:
    uint8_t buffer[SIZE];
    bool bufferFull = false;
    uint32_t bufferEnd = 0; //location of the first open byte of data
    uint32_t bufferStart = 0; //location of the first byte of data
    //uint16_t size = 0;

    
};