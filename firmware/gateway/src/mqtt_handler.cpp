#include "mqtt_handler.h"
#include "buffer.h"
#include <ArduinoJson.h>

// Static instance pointer
MQTTHandler* MQTTHandler::instance = nullptr;

// Global instance
MQTTHandler mqtt;

// Command callback
static CommandReceivedCallback commandCallback = nullptr;

void setCommandReceivedCallback(CommandReceivedCallback cb) {
    commandCallback = cb;
}

// ==================== MQTT HANDLER IMPLEMENTATION ====================

MQTTHandler::MQTTHandler() : client(wifiClient) {
    strcpy(broker, "192.168.1.100");
    port = MQTT_PORT;
    connected = false;
    lastReconnectAttempt = 0;
    instance = this;
}

MQTTHandler* MQTTHandler::getInstance() {
    return instance;
}

void MQTTHandler::setBroker(const char* brokerAddr, int brokerPort) {
    strcpy(broker, brokerAddr);
    port = brokerPort;
    client.setServer(broker, port);
    client.setCallback(MQTTHandler::onMessage);
    client.setBufferSize(MQTT_BUFFER_SIZE);
}

const char* MQTTHandler::getBroker() {
    return broker;
}

bool MQTTHandler::connect() {
    unsigned long now = millis();
    if (now - lastReconnectAttempt < MQTT_RECONNECT_INTERVAL) {
        return false;
    }
    lastReconnectAttempt = now;
    
    Serial.printf("[MQTT] Connecting to %s:%d\n", broker, port);
    
    if (client.connect(GATEWAY_NAME)) {
        Serial.println("[MQTT] Connected!");
        connected = true;
        subscribe();
        
        // Flush buffer if has data
        if (dataBuffer.getCount() > 0) {
            Serial.printf("[MQTT] Flushing buffer: %d records\n", dataBuffer.getCount());
            while (dataBuffer.getCount() > 0) {
                BufferedData_t batch[BATCH_SIZE];
                int count = dataBuffer.popBatch(batch, BATCH_SIZE);
                publishBatch(batch, count);
                delay(100);
            }
        }
        
        return true;
    } else {
        Serial.printf("[MQTT] Failed, rc=%d\n", client.state());
        connected = false;
        return false;
    }
}

void MQTTHandler::disconnect() {
    client.disconnect();
    connected = false;
}

bool MQTTHandler::isConnected() {
    return client.connected();
}

void MQTTHandler::loop() {
    if (client.connected()) {
        client.loop();
        connected = true;
    } else {
        connected = false;
    }
}

void MQTTHandler::subscribe() {
    char topic[64];
    snprintf(topic, sizeof(topic), TOPIC_COMMAND, GATEWAY_ID);
    client.subscribe(topic);
    Serial.printf("[MQTT] Subscribed: %s\n", topic);
}

bool MQTTHandler::publishTelemetry(SensorData_t* data) {
    if (!connected) return false;
    
    char topic[64];
    snprintf(topic, sizeof(topic), TOPIC_TELEMETRY, GATEWAY_ID);
    
    JsonDocument doc;
    doc["node_id"] = data->nodeId;
    doc["device_id"] = data->deviceId;
    doc["temperature"] = data->temperature;
    doc["humidity"] = data->humidity;
    doc["alarm_state"] = data->alarmState;
    doc["cooler_state"] = data->coolerState;
    doc["timestamp"] = data->timestamp;
    doc["gateway_id"] = GATEWAY_ID;
    
    char payload[256];
    serializeJson(doc, payload);
    
    bool success = client.publish(topic, payload);
    if (success) {
        Serial.printf("[MQTT] Published: %s\n", topic);
    }
    return success;
}

bool MQTTHandler::publishBatch(BufferedData_t* batch, int count) {
    if (!connected || count == 0) return false;
    
    char topic[64];
    snprintf(topic, sizeof(topic), TOPIC_BATCH, GATEWAY_ID);
    
    JsonDocument doc;
    doc["gateway_id"] = GATEWAY_ID;
    doc["batch_time"] = millis();
    doc["count"] = count;
    
    JsonArray dataArray = doc["data"].to<JsonArray>();
    
    for (int i = 0; i < count; i++) {
        JsonObject obj = dataArray.add<JsonObject>();
        obj["node_id"] = batch[i].data.nodeId;
        obj["device_id"] = batch[i].data.deviceId;
        obj["temperature"] = batch[i].data.temperature;
        obj["humidity"] = batch[i].data.humidity;
        obj["alarm_state"] = batch[i].data.alarmState;
        obj["cooler_state"] = batch[i].data.coolerState;
        obj["node_timestamp"] = batch[i].data.timestamp;
        obj["gateway_timestamp"] = batch[i].receivedTime;
    }
    
    char payload[4096];
    size_t len = serializeJson(doc, payload, sizeof(payload));
    
    if (len < sizeof(payload)) {
        bool success = client.publish(topic, payload);
        if (success) {
            Serial.printf("[MQTT] Batch sent: %d records\n", count);
        }
        return success;
    }
    
    return false;
}

bool MQTTHandler::publishStatus(const char* status) {
    if (!connected) return false;
    
    char topic[64];
    snprintf(topic, sizeof(topic), TOPIC_STATUS, GATEWAY_ID);
    return client.publish(topic, status);
}

// ==================== STATIC CALLBACK ====================

void MQTTHandler::onMessage(char* topic, byte* payload, unsigned int length) {
    char message[256];
    if (length >= sizeof(message)) length = sizeof(message) - 1;
    memcpy(message, payload, length);
    message[length] = '\0';
    
    Serial.printf("[MQTT] Received: %s\n", message);
    
    CommandData_t cmd;
    
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (error) {
        // Plain text command
        String cmdStr = String(message);
        cmdStr.trim();
        strcpy(cmd.command, cmdStr.c_str());
        cmd.targetDeviceId = 0;
    } else {
        // JSON command
        const char* cmdStr = doc["command"] | "";
        cmd.targetDeviceId = doc["device_id"] | 0;
        strcpy(cmd.command, cmdStr);
    }
    
    Serial.printf("[MQTT] Command: %s\n", cmd.command);
    
    if (commandCallback) {
        commandCallback(&cmd);
    }
}
