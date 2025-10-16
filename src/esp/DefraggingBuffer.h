#pragma once

template <int SIZE, int MAX_ALLOCATIONS>
class DefraggingBuffer {
  public:
    void init() {
      //TODO implement
    }

    const uint8_t& operator[](unsigned int index) { //passthrough to buffer
      return buffer[index];
    }

    uint32_t malloc(uint16_t size) { //try to reserve the space
      if (size > SIZE) return 0xFFFFFFFF;

      //TODO think about how this operates when the buffer is empty

      //find the first open position with enough space
      for (int i = 0; i < this->numAllocations+1; i++) {
        if (openSpaceBetweenAllocations[i] >= size) {
          //open space found! fit it in the metadata and then return the location
          numAllocations++;
          if (i == 0) {
            arrayInsert(&allocationStartPositions, 0, 0);
          } else {
            arrayInsert(&allocationStartPositions, i, allocationStartPositions[i-1] + allocationSizes[i-1]);
          }
          arrayInsert(&allocationSizes, i, size)
          return allocationStartPositions[i-1] + allocationSizes[i-1];
        } 
        //No open spaces were found
        return 0xFFFFFFFF;
      } 
      
    }

    bool free(uint32_t location) {
      //TODO impl
    }


    void defrag(uint8_t startingPosition, uint16_t size) { //defrag the buffer. Then, update the starting positions
      //TODO impl
    }

  private:
    void arrayInsert(uint16_t* array, int position, uint16_t data) {
      //TODO impl
    }

    void arrayPop(uint16_t* array, int position) {
      //TODO impl
    }

    uint8_t buffer[SIZE];
    uint8_t numAllocations;
    uint16_t allocationStartPositions[MAX_ALLOCATIONS];
    uint16_t allocationSizes[MAX_ALLOCATIONS];
    uint16_t openSpaceBetweenAllocations[MAX_ALLOCATIONS + 1];
}