#pragma once

template <int SIZE, int MAX_ALLOCATIONS>
class DefraggingBuffer {
  public:
    void init() {
      numAllocations = 0;
      openSpaceBetweenAllocations[0] = SIZE;
    }

    uint8_t& operator[](unsigned int index) { //passthrough to buffer
      return buffer[index];
    }

    uint32_t malloc(uint16_t size) { //try to reserve the space
      if (size > SIZE) return 0xFFFFFFFF;

      if (numAllocations == MAX_ALLOCATIONS) return 0xFFFFFFFF;

      //find the first open position with enough space
      for (int i = 0; i < this->numAllocations+1; i++) {
        if (openSpaceBetweenAllocations[i] >= size) {
          //open space found! fit it in the metadata and then return the location
          uint32_t ret;
          if (i == 0) {
            arrayInsert(&(allocationStartPositions[0]), numAllocations, 0, 0);
            ret = 0;
          } else {
            arrayInsert(&(allocationStartPositions[0]), numAllocations, i, allocationStartPositions[i-1] + allocationSizes[i-1]);
            ret = allocationStartPositions[i-1] + allocationSizes[i-1];

          }
          arrayInsert(&(allocationSizes[0]), numAllocations, i, size);
          

          //make sure the openSpaceBetweenAllocations table gets updated
          arrayInsert(&(openSpaceBetweenAllocations[0]), numAllocations+1, i, 0);
          numAllocations++;

          return ret;
        } 
        //No open spaces were found
        return 0xFFFFFFFF;
      } 
      return 0xFFFFFFFF;
      
    }

    bool free(uint32_t location) {
      //find the start position index in the allocationStartPositions array
      for (int i = 0; i < numAllocations; i++) {
        if (location == allocationStartPositions[i]) {
          //we found the index of the allocation, lets remove it and then combine the surrounding open space plus the size of the allocation
          uint32_t newSize = openSpaceBetweenAllocations[i] + openSpaceBetweenAllocations[i+1] + allocationSizes[i];
          arrayPop(&(openSpaceBetweenAllocations[0]), numAllocations, i);
          arrayPop(&(allocationSizes[0]), numAllocations, i);
          arrayPop(&(allocationStartPositions[0]), numAllocations+1, i);
          openSpaceBetweenAllocations[i] = newSize;
          numAllocations--;
          return true;
        }
      }

      //if we got here, then something went wrong, the location asked for was never found
      return false;
    }


    void defrag(uint8_t* startingPositions, uint16_t size) { //defrag the buffer. Then, update the starting positions
      //we want to move each allocation and then updates its internal start position. Then, after updating the start position, we want to find the corresponding start position
      //in the startingPositions array and modify them accordingly
      //NOTE implement only if needed
    }

  private:
    void arrayInsert(uint16_t* array, uint16_t arraySize, int position, uint16_t data) {
      //move all elements in the array over
      for (int i = arraySize-1; i >= position; i--) {
        array[i+1] = array[i];
      }
      array[position] = data;
    }

    void arrayPop(uint16_t* array, uint16_t arraySize, int position) {
      for (int i = position; i < arraySize; i++) {
        array[i] = array[i+1];
      }
    }

    uint8_t buffer[SIZE];
    uint8_t numAllocations;
    uint16_t allocationStartPositions[MAX_ALLOCATIONS];
    uint16_t allocationSizes[MAX_ALLOCATIONS];
    uint16_t openSpaceBetweenAllocations[MAX_ALLOCATIONS + 1];
};