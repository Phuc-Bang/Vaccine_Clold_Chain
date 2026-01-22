#include "sensor.h"

// Global instance
SensorHandler sensor;

// ==================== SENSOR HANDLER IMPLEMENTATION ====================

SensorHandler::SensorHandler() : dht(DHT_PIN, DHT_TYPE) {
    bufferIndex = 0;
    bufferFull = false;
    memset(tempBuffer, 0, sizeof(tempBuffer));
}

void SensorHandler::init() {
    dht.begin();
    Serial.println("[SENSOR] DHT11 initialized");
}

bool SensorHandler::read(float* temperature, float* humidity) {
    float temp = dht.readTemperature();
    float hum = dht.readHumidity();
    
    if (isnan(temp) || isnan(hum)) {
        Serial.println("[SENSOR] Error reading DHT!");
        return false;
    }
    
    *temperature = temp;
    *humidity = hum;
    
    // Add to filter
    addToFilter(temp);
    
    return true;
}

void SensorHandler::addToFilter(float temp) {
    tempBuffer[bufferIndex] = temp;
    bufferIndex++;
    
    if (bufferIndex >= MEDIAN_FILTER_SIZE) {
        bufferIndex = 0;
        bufferFull = true;
    }
}

float SensorHandler::getMedian() {
    float sorted[MEDIAN_FILTER_SIZE];
    int count = bufferFull ? MEDIAN_FILTER_SIZE : bufferIndex;
    
    if (count == 0) return 0;
    
    // Copy buffer
    for (int i = 0; i < count; i++) {
        sorted[i] = tempBuffer[i];
    }
    
    // Bubble sort (simple for small array)
    for (int i = 0; i < count - 1; i++) {
        for (int j = 0; j < count - i - 1; j++) {
            if (sorted[j] > sorted[j + 1]) {
                float temp = sorted[j];
                sorted[j] = sorted[j + 1];
                sorted[j + 1] = temp;
            }
        }
    }
    
    return sorted[count / 2];
}

float SensorHandler::getFilteredTemperature() {
    return getMedian();
}
