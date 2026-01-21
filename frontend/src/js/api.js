/**
 * Vaccine Cold Chain Monitoring - API Module
 * Handles API calls to backend
 */

class ApiClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    async sendCommand(gatewayId, command, deviceId = null) {
        try {
            const response = await fetch(`${this.baseUrl}/api/command/${gatewayId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    command: command,
                    device_id: deviceId
                })
            });
            return await response.json();
        } catch (error) {
            console.error('[API] Error:', error);
            return { ok: false, error: error.message };
        }
    }

    async getDevices() {
        try {
            const response = await fetch(`${this.baseUrl}/api/devices`);
            return await response.json();
        } catch (error) {
            console.error('[API] Error:', error);
            return { devices: [] };
        }
    }

    async getTelemetry(deviceId = null, limit = 100) {
        try {
            let url = `${this.baseUrl}/api/telemetry?limit=${limit}`;
            if (deviceId) url += `&device_id=${deviceId}`;
            const response = await fetch(url);
            return await response.json();
        } catch (error) {
            console.error('[API] Error:', error);
            return { data: [] };
        }
    }

    async getAlerts() {
        try {
            const response = await fetch(`${this.baseUrl}/api/alerts`);
            return await response.json();
        } catch (error) {
            console.error('[API] Error:', error);
            return { alerts: [] };
        }
    }

    async acknowledgeAlert(alertId) {
        try {
            const response = await fetch(`${this.baseUrl}/api/alerts/${alertId}/acknowledge`, {
                method: 'POST'
            });
            return await response.json();
        } catch (error) {
            console.error('[API] Error:', error);
            return { ok: false };
        }
    }

    async getStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/api/status`);
            return await response.json();
        } catch (error) {
            console.error('[API] Error:', error);
            return { mqtt_connected: false };
        }
    }
}

// Export for use
window.ApiClient = ApiClient;
