#ifndef ESPNOW_HANDLER_H
#define ESPNOW_HANDLER_H

#include <Arduino.h>
#include <esp_now.h>
#include "config.h"

// ==================== ESP-NOW MODULE ====================

// Node management
#define MAX_NODES 10

class ESPNowHandler {
private:
    uint8_t nodePeers[MAX_NODES][6];
    int nodeCount;
    
    static ESPNowHandler* instance;
    
public:
    ESPNowHandler();
    
    bool init();
    bool addPeer(const uint8_t* mac);
    bool removePeer(const uint8_t* mac);
    bool sendToNode(const uint8_t* mac, CommandData_t* cmd);
    bool sendToAllNodes(CommandData_t* cmd);
    bool broadcast(CommandData_t* cmd);
    
    int getNodeCount();
    bool isNodeRegistered(const uint8_t* mac);
    
    // Callbacks (static for ESP-NOW)
    static void onDataReceived(const uint8_t* mac, const uint8_t* data, int len);
    static void onDataSent(const uint8_t* mac, esp_now_send_status_t status);
    
    static ESPNowHandler* getInstance();
};

// Global instance
extern ESPNowHandler espNow;

// Callback for received data (to be set by main)
typedef void (*DataReceivedCallback)(SensorData_t* data, const uint8_t* mac);
void setDataReceivedCallback(DataReceivedCallback cb);

#endif // ESPNOW_HANDLER_H
