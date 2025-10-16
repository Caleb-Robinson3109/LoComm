#pragma once

//we assume that the first byte is an identifier we plan to search, and the rest of the bytes in each unit is just general data

template <int SIZE, int UNIT_SIZE>
class SimpleArraySet {
  public:
    uint32_t size() return length;

    uint8_t* get(int i) return (&buffer) + i*UNIT_SIZE;

    uint16_t find(int8_t startByte) {
      return 65535; //TODO implement
    }

    bool add(int8_t* src) {
      return true; //TODO impl
    }

    bool remove(int index) {
      return true; //TODO impl
    }

    



  private:
    uint8_t buffer[SIZE * UNIT_SIZE];
    uint32_t length = 0;
}