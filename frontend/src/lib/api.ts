import axios from 'axios';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

export interface Telemetry {
    id: number;
    node_id: string;
    temperature: number;
    humidity: number;
    timestamp: string;
    battery_level?: number;
    signal_strength?: number;
}

export const getTelemetry = async () => {
    const response = await api.get<Telemetry[]>('/telemetry');
    return response.data;
};

export default api;
