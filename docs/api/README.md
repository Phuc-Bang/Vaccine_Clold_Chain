# API Documentation

## Overview

VaccineColdChain API provides endpoints for managing vaccine cold chain monitoring system.

## Authentication

All endpoints require authentication via JWT token (coming in v2.0).

## Base URL

```
http://localhost:8000/api
```

## Endpoints

### Devices

- `GET /devices` - List all devices
- `GET /devices/<device_id>` - Get device details
- `POST /devices` - Create new device
- `PUT /devices/<device_id>` - Update device
- `DELETE /devices/<device_id>` - Delete device

### Telemetry

- `GET /devices/<device_id>/telemetry` - Get telemetry data
- `GET /devices/<device_id>/telemetry/latest` - Get latest telemetry
- `POST /devices/<device_id>/telemetry` - Save telemetry data

### Alarms

- `GET /devices/<device_id>/alarms` - Get device alarms
- `POST /devices/<device_id>/alarms` - Create alarm (coming soon)

### Health

- `GET /health` - API health check

## Response Format

All responses are in JSON format:

```json
{
  "success": true,
  "data": {},
  "message": "Operation successful"
}
```

## Error Handling

Errors return appropriate HTTP status codes:

- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Rate limiting coming in v2.0 (100 requests/minute per device).

## Pagination

List endpoints support pagination (coming in v2.0):

- `?page=1&limit=20`
