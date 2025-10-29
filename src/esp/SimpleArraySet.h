#pragma once

//we assume that the first byte and second byte are identifiers we plan to search, and the rest of the bytes in each unit is just general data

template <int SIZE, int UNIT_SIZE>
class SimpleArraySet {
  public:
    uint32_t size() {
      return length;
    }

    uint8_t* get(int i) {
      return (&(buffer[0])) + i*UNIT_SIZE;
    }
    uint16_t find(uint8_t firstByte, uint8_t secondByte) {
      for (int i = 0; i < length; i++) {
        if (buffer[UNIT_SIZE * i] == firstByte && buffer[UNIT_SIZE * i + 1] == secondByte) return i;
      }
      return 65535;
    }

    bool add(uint8_t* src) {
      if (length == SIZE) return false; //buffer full!
      memcpy(&(buffer[length * UNIT_SIZE]), src, UNIT_SIZE);
      length++;
      return true; 
    }

    bool remove(uint16_t index) {
      if (index >= length) return false; //invalid index
      //if the index we are removing is at the very end, just shorten length
      if (index == length - 1) {
        length--;
        return true;
      } else {
        //otherwise, replace the index being removed with the final unit
        memcpy(&(buffer[index * UNIT_SIZE]), &(buffer[(length-1)*UNIT_SIZE]), UNIT_SIZE);
        length--;
        return true;
      }
    }

    void clearAll() {
      length = 0;
    }

  private:
    uint8_t buffer[SIZE * UNIT_SIZE];
    uint32_t length = 0;
};