-- Schema cho ColdChain Dashboard Database
-- File: database/schema.sql

-- Bảng lưu trữ dữ liệu nhiệt độ từ cảm biến
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id TEXT NOT NULL,              -- ID của thiết bị (ví dụ: NODE_01)
    sensor_value REAL NOT NULL,         -- Giá trị nhiệt độ (°C)
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Thời gian ghi nhận
    sensor_type TEXT DEFAULT 'temperature'         -- Loại cảm biến
);

-- Index để truy vấn nhanh theo node_id và timestamp
CREATE INDEX IF NOT EXISTS idx_node_timestamp 
ON measurements(node_id, timestamp DESC);

-- Bảng lưu trữ lịch sử điều khiển thiết bị
CREATE TABLE IF NOT EXISTS control_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,            -- ID thiết bị được điều khiển
    command TEXT NOT NULL,              -- Lệnh: ON/OFF
    param INTEGER,                      -- Tham số (ví dụ: công suất %)
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'sent'          -- sent/confirmed/failed
);

-- Index cho control_logs
CREATE INDEX IF NOT EXISTS idx_device_control 
ON control_logs(device_id, timestamp DESC);

-- Insert dữ liệu mẫu để test
INSERT INTO measurements (node_id, sensor_value, timestamp) VALUES
('NODE_01', 4.5, datetime('now', '-10 minutes')),
('NODE_01', 5.2, datetime('now', '-9 minutes')),
('NODE_01', 4.8, datetime('now', '-8 minutes')),
('NODE_01', 5.5, datetime('now', '-7 minutes')),
('NODE_01', 6.1, datetime('now', '-6 minutes')),
('NODE_01', 5.8, datetime('now', '-5 minutes')),
('NODE_01', 5.3, datetime('now', '-4 minutes')),
('NODE_01', 4.9, datetime('now', '-3 minutes')),
('NODE_01', 5.6, datetime('now', '-2 minutes')),
('NODE_01', 5.2, datetime('now', '-1 minutes'));
