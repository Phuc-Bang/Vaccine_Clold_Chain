#ifndef CONFIG_H
#define CONFIG_H

// ==================== DEVICE INFO ====================
#define GATEWAY_ID          1
#define GATEWAY_NAME        "VaccineGateway_01"

// ==================== HARDWARE PINS ====================
#define LED_STATUS          2       // LED onboard
#define RESET_BUTTON        0       // BOOT button (GPIO 0)

// ==================== MQTT CONFIG ====================
#define MQTT_PORT           1883
// Note: MQTT_KEEPALIVE is already defined in PubSubClient (15 seconds)
#define MQTT_BUFFER_SIZE    4096

// MQTT Topics Template
#define TOPIC_TELEMETRY     "vaccine/gateway/%d/telemetry"
#define TOPIC_BATCH         "vaccine/gateway/%d/batch"
#define TOPIC_COMMAND       "vaccine/gateway/%d/command"
#define TOPIC_STATUS        "vaccine/gateway/%d/status"

// ==================== WIFI CONFIG ====================
#define WIFI_AP_SSID        "VaccineGateway_Setup"
#define WIFI_AP_PASSWORD    "vaccine123"
#define WIFI_PORTAL_TIMEOUT 180     // seconds

// ==================== BUFFER CONFIG ====================
#define BUFFER_SIZE         200     // Circular buffer size
#define BATCH_SIZE          50      // Records per batch

// ==================== TIMING CONFIG ====================
#define MQTT_RECONNECT_INTERVAL     5000    // ms
#define BATCH_SEND_INTERVAL         30000   // ms
#define STATUS_PRINT_INTERVAL       10000   // ms

// ==================== DATA STRUCTURES ====================

// Sensor data from Node -> Gateway
typedef struct {
    char nodeId[16];
    int deviceId;
    float temperature;
    float humidity;
    bool alarmState;
    bool coolerState;
    unsigned long timestamp;
} SensorData_t;

// Buffered data with receive time
typedef struct {
    SensorData_t data;
    unsigned long receivedTime;
    bool sent;
} BufferedData_t;

// Command from Server -> Gateway -> Node
typedef struct {
    char command[32];
    int targetDeviceId;
} CommandData_t;

#endif // CONFIG_H
