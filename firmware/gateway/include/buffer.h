#ifndef BUFFER_H
#define BUFFER_H

#include <Arduino.h>
#include "config.h"

// ==================== CIRCULAR BUFFER MODULE ====================

class CircularBuffer {
private:
    BufferedData_t buffer[BUFFER_SIZE];
    int head;
    int tail;
    int count;

public:
    CircularBuffer();
    
    bool push(SensorData_t* data);
    bool pop(BufferedData_t* out);
    bool peek(int index, BufferedData_t* out);
    
    int getCount();
    bool isEmpty();
    bool isFull();
    void clear();
    
    // Get multiple items for batch send
    int popBatch(BufferedData_t* outArray, int maxCount);
};

// Global buffer instance
extern CircularBuffer dataBuffer;

#endif // BUFFER_H
