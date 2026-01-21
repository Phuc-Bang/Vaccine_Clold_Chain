#include "espnow_comm.h"

// Static instance pointer
ESPNowComm* ESPNowComm::instance = nullptr;

// Global instance
ESPNowComm espNow;

// Command callback
static CommandCallback cmdCallback = nullptr;

void setCommandCallback(CommandCallback cb) {
    cmdCallback = cb;
}

// ==================== ESP-NOW COMM IMPLEMENTATION ====================

ESPNowComm::ESPNowComm() {
    uint8_t mac[] = GATEWAY_MAC;
    memcpy(gatewayMAC, mac, 6);
    connected = false;
    lastResponse = 0;
    instance = this;
}

ESPNowComm* ESPNowComm::getInstance() {
    return instance;
}

bool ESPNowComm::init() {
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    
    Serial.print("[ESP-NOW] Node MAC: ");
    Serial.println(WiFi.macAddress());
    
    Serial.print("[ESP-NOW] Gateway MAC: ");
    Serial.printf("%02X:%02X:%02X:%02X:%02X:%02X\n",
        gatewayMAC[0], gatewayMAC[1], gatewayMAC[2],
        gatewayMAC[3], gatewayMAC[4], gatewayMAC[5]);
    
    if (esp_now_init() != ESP_OK) {
        Serial.println("[ESP-NOW] Init failed!");
        return false;
    }
    
    // Register callbacks
    esp_now_register_send_cb(ESPNowComm::onDataSent);
    esp_now_register_recv_cb(ESPNowComm::onDataReceived);
    
    // Add gateway peer
    esp_now_peer_info_t peerInfo = {};
    memcpy(peerInfo.peer_addr, gatewayMAC, 6);
    peerInfo.channel = 0;
    peerInfo.encrypt = false;
    
    if (esp_now_add_peer(&peerInfo) != ESP_OK) {
        Serial.println("[ESP-NOW] Add peer failed!");
        return false;
    }
    
    Serial.println("[ESP-NOW] Initialized OK");
    return true;
}

bool ESPNowComm::send(SensorData_t* data) {
    esp_err_t result = esp_now_send(gatewayMAC, (uint8_t*)data, sizeof(SensorData_t));
    return result == ESP_OK;
}

bool ESPNowComm::isConnected() {
    return connected;
}

void ESPNowComm::updateConnectionStatus(bool success) {
    if (success) {
        connected = true;
        lastResponse = millis();
    }
}

void ESPNowComm::checkTimeout() {
    if (millis() - lastResponse > GATEWAY_TIMEOUT) {
        connected = false;
    }
}

// ==================== STATIC CALLBACKS ====================

void ESPNowComm::onDataSent(const uint8_t* mac, esp_now_send_status_t status) {
    ESPNowComm* self = ESPNowComm::getInstance();
    if (!self) return;
    
    bool success = (status == ESP_NOW_SEND_SUCCESS);
    self->updateConnectionStatus(success);
    
    Serial.printf("[ESP-NOW] Send: %s\n", success ? "OK" : "FAIL");
}

void ESPNowComm::onDataReceived(const uint8_t* mac, const uint8_t* data, int len) {
    ESPNowComm* self = ESPNowComm::getInstance();
    if (!self) return;
    
    if (len == sizeof(CommandData_t)) {
        CommandData_t cmd;
        memcpy(&cmd, data, sizeof(CommandData_t));
        
        Serial.printf("[ESP-NOW] Received command: %s\n", cmd.command);
        
        self->updateConnectionStatus(true);
        
        if (cmdCallback) {
            cmdCallback(&cmd);
        }
    }
}
