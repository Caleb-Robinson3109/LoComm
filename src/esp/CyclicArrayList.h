#pragma once

//TODO this could be optimized by actually tracking size instead of calculating it

template <typename T, int SIZE>
class CyclicArrayList {
  public:
    //CyclicArrayList();

    const T& operator[](unsigned int index) {
      if (index >= SIZE) {
        return buffer[0]; //TODO this is not ideal, but there is no error handling
      } else {
        index += bufferStart;
        if (index >= SIZE) index -= SIZE;
        return buffer[index];
      }
    }

    bool contains(T value) {
      if (!bufferFull && bufferStart == bufferEnd) return false;
      if (bufferStart < bufferEnd) {
        for (int i = bufferStart; i < bufferEnd; i++) {
          if (buffer[i] == value) return true;
        }
      } else if (bufferStart > bufferEnd) {
        for (int i = bufferStart; i < SIZE; i++) {
          if (buffer[i] == value) return true;
        }
        for (int i = 0; i < bufferEnd; i++) {
          if (buffer[i] == value) return true;
        }
      } else {
        for (int i = 0; i < SIZE; i++) {
          if (buffer[i] == value) return true;
        }
      }
      return false;
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

    bool pushBack(const T* src, int size) { //TODO need to put a lock around this
      if (size > this->spaceLeft()) return false;
      
      if (SIZE - bufferEnd < size) { //If adding to the buffer would wrap it around...
        memcpy(&(buffer[bufferEnd]), src, sizeof(T) * (SIZE - bufferEnd));
        memcpy(buffer, src, sizeof(T) * (size - (SIZE - bufferEnd)));
        bufferEnd = (size - (SIZE - bufferEnd));
      } else { 
        memcpy(&(buffer[bufferEnd]), src, sizeof(T) * (size));
        bufferEnd += size;
      }
      return true;
    }

    bool pushBackSingle(T value) {
      if (this->spaceLeft() == 0) return false;
      buffer[bufferEnd++] = value;
      if (bufferEnd == SIZE) bufferEnd = 0;
      return true;
    }

    bool peakFront(T* dst, int s) {
      if (s > this->size()) {
        return false;
      }
      uint16_t readEnd = bufferStart + s;
      if (readEnd > SIZE) {
        //buffer is overlapped, will need to memcpy operations
        memcpy(&(dst[0]), &(buffer[bufferStart]), SIZE - bufferStart);
        memcpy(&(dst[SIZE-bufferStart]), &(buffer[0]), s - (SIZE - bufferStart));
      } else {
        memcpy(&(dst[0]), &(buffer[bufferStart]), s);
      }
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

    void clearBuffer() {
      bufferStart = 0;
      bufferEnd = 0;
    }

  private:
    T buffer[SIZE];
    bool bufferFull = false;
    uint32_t bufferEnd = 0; //location of the first open byte of data
    uint32_t bufferStart = 0; //location of the first byte of data
    //uint16_t size = 0;

    
};