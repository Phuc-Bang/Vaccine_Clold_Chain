#include "espnow_handler.h"
#include <WiFi.h>

// Static instance pointer
ESPNowHandler* ESPNowHandler::instance = nullptr;

// Global instance
ESPNowHandler espNow;

// Data callback
static DataReceivedCallback dataCallback = nullptr;

void setDataReceivedCallback(DataReceivedCallback cb) {
    dataCallback = cb;
}

// ==================== ESP-NOW HANDLER IMPLEMENTATION ====================

ESPNowHandler::ESPNowHandler() {
    nodeCount = 0;
    instance = this;
    memset(nodePeers, 0, sizeof(nodePeers));
}

ESPNowHandler* ESPNowHandler::getInstance() {
    return instance;
}

bool ESPNowHandler::init() {
    WiFi.mode(WIFI_STA);
    
    Serial.print("[ESP-NOW] MAC Address: ");
    Serial.println(WiFi.macAddress());
    
    if (esp_now_init() != ESP_OK) {
        Serial.println("[ESP-NOW] Init failed!");
        return false;
    }
    
    // Register callbacks
    esp_now_register_recv_cb(ESPNowHandler::onDataReceived);
    esp_now_register_send_cb(ESPNowHandler::onDataSent);
    
    // Add broadcast peer
    uint8_t broadcastMAC[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    addPeer(broadcastMAC);
    
    Serial.println("[ESP-NOW] Initialized OK");
    return true;
}

bool ESPNowHandler::addPeer(const uint8_t* mac) {
    esp_now_peer_info_t peerInfo = {};
    memcpy(peerInfo.peer_addr, mac, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;
    
    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("[ESP-NOW] Add peer failed");
        return false;
    }
    return true;
}

bool ESPNowHandler::removePeer(const uint8_t* mac) {
    return esp_now_del_peer(mac) == ESP_OK;
}

bool ESPNowHandler::isNodeRegistered(const uint8_t* mac) {
    for (int i = 0; i < nodeCount; i++) {
        if (memcmp(nodePeers[i], mac, 6) == 0) {
            return true;
        }
    }
    return false;
}

int ESPNowHandler::getNodeCount() {
    return nodeCount;
}

bool ESPNowHandler::sendToNode(const uint8_t* mac, CommandData_t* cmd) {
    esp_err_t result = esp_now_send(mac, (uint8_t*)cmd, sizeof(CommandData_t));
    return result == ESP_OK;
}

bool ESPNowHandler::sendToAllNodes(CommandData_t* cmd) {
    bool success = true;
    for (int i = 0; i < nodeCount; i++) {
        if (!sendToNode(nodePeers[i], cmd)) {
            success = false;
        }
    }
    return success;
}

bool ESPNowHandler::broadcast(CommandData_t* cmd) {
    uint8_t broadcastMAC[6] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
    return sendToNode(broadcastMAC, cmd);
}

// ==================== STATIC CALLBACKS ====================

void ESPNowHandler::onDataReceived(const uint8_t* mac, const uint8_t* data, int len) {
    ESPNowHandler* self = ESPNowHandler::getInstance();
    if (!self) return;
    
    if (len == sizeof(SensorData_t)) {
        SensorData_t receivedData;
        memcpy(&receivedData, data, sizeof(SensorData_t));
        
        // Register new node
        if (!self->isNodeRegistered(mac) && self->nodeCount < MAX_NODES) {
            memcpy(self->nodePeers[self->nodeCount], mac, 6);
            self->nodeCount++;
            self->addPeer(mac);
            
            Serial.printf("[ESP-NOW] New node registered. Total: %d\n", self->nodeCount);
        }
        
        // Call user callback
        if (dataCallback) {
            dataCallback(&receivedData, mac);
        }
    }
}

void ESPNowHandler::onDataSent(const uint8_t* mac, esp_now_send_status_t status) {
    Serial.printf("[ESP-NOW] Send: %s\n", 
        status == ESP_NOW_SEND_SUCCESS ? "OK" : "FAIL");
}
