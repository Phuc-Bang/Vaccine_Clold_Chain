#ifndef ESPNOW_COMM_H
#define ESPNOW_COMM_H

#include <Arduino.h>
#include <esp_now.h>
#include <WiFi.h>
#include "config.h"

// ==================== ESP-NOW COMMUNICATION MODULE ====================

class ESPNowComm {
private:
    uint8_t gatewayMAC[6];
    bool connected;
    unsigned long lastResponse;
    
    static ESPNowComm* instance;
    
public:
    ESPNowComm();
    
    bool init();
    bool send(SensorData_t* data);
    
    bool isConnected();
    void updateConnectionStatus(bool success);
    void checkTimeout();
    
    // Static callbacks
    static void onDataSent(const uint8_t* mac, esp_now_send_status_t status);
    static void onDataReceived(const uint8_t* mac, const uint8_t* data, int len);
    
    static ESPNowComm* getInstance();
};

// Global instance
extern ESPNowComm espNow;

// Callback for received commands
typedef void (*CommandCallback)(CommandData_t* cmd);
void setCommandCallback(CommandCallback cb);

#endif // ESPNOW_COMM_H
