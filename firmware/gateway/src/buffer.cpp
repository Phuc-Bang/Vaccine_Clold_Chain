#include "buffer.h"

// Global instance
CircularBuffer dataBuffer;

// ==================== CIRCULAR BUFFER IMPLEMENTATION ====================

CircularBuffer::CircularBuffer() {
    head = 0;
    tail = 0;
    count = 0;
}

bool CircularBuffer::push(SensorData_t* data) {
    if (count >= BUFFER_SIZE) {
        // Buffer full, overwrite oldest
        Serial.println("[BUFFER] Full! Overwriting oldest");
        tail = (tail + 1) % BUFFER_SIZE;
        count--;
    }
    
    buffer[head].data = *data;
    buffer[head].receivedTime = millis();
    buffer[head].sent = false;
    
    head = (head + 1) % BUFFER_SIZE;
    count++;
    
    Serial.printf("[BUFFER] Added. Total: %d/%d\n", count, BUFFER_SIZE);
    return true;
}

bool CircularBuffer::pop(BufferedData_t* out) {
    if (count == 0) return false;
    
    *out = buffer[tail];
    tail = (tail + 1) % BUFFER_SIZE;
    count--;
    
    return true;
}

bool CircularBuffer::peek(int index, BufferedData_t* out) {
    if (index >= count) return false;
    
    int actualIndex = (tail + index) % BUFFER_SIZE;
    *out = buffer[actualIndex];
    return true;
}

int CircularBuffer::getCount() {
    return count;
}

bool CircularBuffer::isEmpty() {
    return count == 0;
}

bool CircularBuffer::isFull() {
    return count >= BUFFER_SIZE;
}

void CircularBuffer::clear() {
    head = 0;
    tail = 0;
    count = 0;
}

int CircularBuffer::popBatch(BufferedData_t* outArray, int maxCount) {
    int popped = 0;
    
    while (popped < maxCount && count > 0) {
        outArray[popped] = buffer[tail];
        tail = (tail + 1) % BUFFER_SIZE;
        count--;
        popped++;
    }
    
    return popped;
}
