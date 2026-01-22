/**
 * @file protocol_defs.h
 * @brief Shared protocol definitions between Node and Gateway
 * @version 1.0.0
 */

#ifndef PROTOCOL_DEFS_H
#define PROTOCOL_DEFS_H

#include <stdint.h>

// ============================================================================
// SYSTEM CONSTANTS
// ============================================================================

#define DEVICE_TYPE_NODE        0x01
#define DEVICE_TYPE_GATEWAY     0x02

#define MSG_TYPE_TELEMETRY      0x10
#define MSG_TYPE_ALERT          0x20
#define MSG_TYPE_COMMAND        0x30
#define MSG_TYPE_ACK            0x40

// Temperature thresholds (°C)
#define TEMP_MIN_SAFE           2.0f
#define TEMP_MAX_SAFE           8.0f
#define TEMP_CRITICAL_HIGH      10.0f
#define TEMP_CRITICAL_LOW       0.0f

// Timing (milliseconds)
#define TELEMETRY_INTERVAL_MS   5000
#define HEARTBEAT_INTERVAL_MS   30000
#define BUFFER_SYNC_INTERVAL_MS 60000

// ============================================================================
// DATA STRUCTURES
// ============================================================================

/**
 * @brief Telemetry data packet from sensor node
 */
typedef struct __attribute__((packed)) {
    uint8_t  msg_type;          // MSG_TYPE_TELEMETRY
    uint8_t  node_id;           // Node identifier (1-255)
    float    temperature;       // Temperature in Celsius
    float    humidity;          // Humidity in %
    uint32_t timestamp;         // Unix timestamp
    uint8_t  battery_level;     // Battery % (0-100)
    uint8_t  signal_strength;   // RSSI value
} TelemetryPacket;

/**
 * @brief Alert packet for temperature violations
 */
typedef struct __attribute__((packed)) {
    uint8_t  msg_type;          // MSG_TYPE_ALERT
    uint8_t  node_id;           // Node identifier
    uint8_t  alert_type;        // 0=HIGH_TEMP, 1=LOW_TEMP, 2=SENSOR_FAIL
    float    current_value;     // Current temperature
    float    threshold;         // Violated threshold
    uint32_t timestamp;         // When alert triggered
} AlertPacket;

/**
 * @brief Command packet from server to node
 */
typedef struct __attribute__((packed)) {
    uint8_t  msg_type;          // MSG_TYPE_COMMAND
    uint8_t  target_node;       // Target node (0 = broadcast)
    uint8_t  command;           // Command code
    uint8_t  param;             // Command parameter
} CommandPacket;

// Command codes
#define CMD_RESET_ALARM         0x01
#define CMD_SET_INTERVAL        0x02
#define CMD_REBOOT              0x03
#define CMD_OTA_UPDATE          0x04

// ============================================================================
// HELPER MACROS
// ============================================================================

#define IS_TEMP_SAFE(t)         ((t) >= TEMP_MIN_SAFE && (t) <= TEMP_MAX_SAFE)
#define IS_TEMP_CRITICAL(t)     ((t) >= TEMP_CRITICAL_HIGH || (t) <= TEMP_CRITICAL_LOW)

#endif // PROTOCOL_DEFS_H
