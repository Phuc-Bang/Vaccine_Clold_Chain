#ifndef SENSOR_H
#define SENSOR_H

#include <Arduino.h>
#include <DHT.h>
#include "config.h"

// ==================== SENSOR MODULE ====================

class SensorHandler {
private:
    DHT dht;
    
    // Median filter buffer
    float tempBuffer[MEDIAN_FILTER_SIZE];
    int bufferIndex;
    bool bufferFull;
    
    float getMedian();
    
public:
    SensorHandler();
    
    void init();
    bool read(float* temperature, float* humidity);
    float getFilteredTemperature();
    void addToFilter(float temp);
};

// Global instance
extern SensorHandler sensor;

#endif // SENSOR_H
