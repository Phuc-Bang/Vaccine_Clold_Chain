#ifndef MQTT_HANDLER_H
#define MQTT_HANDLER_H

#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include "config.h"

// ==================== MQTT MODULE ====================

class MQTTHandler {
private:
    WiFiClient wifiClient;
    PubSubClient client;
    
    char broker[64];
    int port;
    bool connected;
    unsigned long lastReconnectAttempt;
    
    static MQTTHandler* instance;
    
public:
    MQTTHandler();
    
    void setBroker(const char* brokerAddr, int brokerPort = MQTT_PORT);
    const char* getBroker();
    
    bool connect();
    void disconnect();
    bool isConnected();
    void loop();
    
    bool publishTelemetry(SensorData_t* data);
    bool publishBatch(BufferedData_t* batch, int count);
    bool publishStatus(const char* status);
    
    void subscribe();
    
    // Static callback for PubSubClient
    static void onMessage(char* topic, byte* payload, unsigned int length);
    
    static MQTTHandler* getInstance();
};

// Global instance
extern MQTTHandler mqtt;

// Callback for commands (to be set by main)
typedef void (*CommandReceivedCallback)(CommandData_t* cmd);
void setCommandReceivedCallback(CommandReceivedCallback cb);

#endif // MQTT_HANDLER_H
