"""
Vaccine Cold Chain Monitoring - Database Module
Lưu trữ dữ liệu nhiệt độ, thiết bị, và cảnh báo vào SQLite
"""

import sqlite3
import threading
from datetime import datetime
from typing import List, Optional, Dict
from contextlib import contextmanager

DB_PATH = "vaccine_coldchain.db"
_lock = threading.Lock()


def get_connection():
    """Tạo kết nối database với row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Khởi tạo database và các bảng"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Bảng thiết bị (devices) - Danh sách kho
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                location TEXT,
                type TEXT DEFAULT 'cold_storage',
                temp_min REAL DEFAULT 20.0,
                temp_max REAL DEFAULT 30.0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Bảng telemetry (time-series) - Lịch sử nhiệt độ
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                gateway_id INTEGER,
                temperature REAL NOT NULL,
                humidity REAL,
                alarm_state BOOLEAN DEFAULT 0,
                cooler_state BOOLEAN DEFAULT 0,
                node_timestamp INTEGER,
                gateway_timestamp INTEGER,
                measured_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)
        
        # Bảng alerts - Lịch sử cảnh báo
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL,
                temperature REAL,
                message TEXT,
                acknowledged BOOLEAN DEFAULT 0,
                acknowledged_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices(device_id)
            )
        """)
        
        # Bảng commands - Lịch sử lệnh điều khiển
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                gateway_id INTEGER,
                command TEXT NOT NULL,
                status TEXT DEFAULT 'sent',
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        # Index cho query nhanh
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_telemetry_device_time 
            ON telemetry(device_id, created_at DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_device 
            ON alerts(device_id, created_at DESC)
        """)
        
        # Thêm dữ liệu mẫu nếu chưa có
        cursor.execute("SELECT COUNT(*) FROM devices")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO devices (device_id, name, location, type) VALUES
                (1, 'Kho A', 'Tầng 1 - Phòng 101', 'cold_storage'),
                (2, 'Kho B', 'Tầng 1 - Phòng 102', 'cold_storage'),
                (3, 'Kho C', 'Tầng 2 - Phòng 201', 'cold_storage')
            """)
            print("[DB] Đã thêm dữ liệu mẫu devices")
        
        conn.commit()
        conn.close()
        print("[DB] Database initialized: " + DB_PATH)


# ==================== DEVICE FUNCTIONS ====================

def get_all_devices() -> List[Dict]:
    """Lấy danh sách tất cả thiết bị"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices ORDER BY device_id")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def get_device(device_id: int) -> Optional[Dict]:
    """Lấy thông tin một thiết bị"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE device_id = ?", (device_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None


def add_device(device_id: int, name: str, location: str = None) -> bool:
    """Thêm thiết bị mới"""
    with _lock:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO devices (device_id, name, location) VALUES (?, ?, ?)",
                (device_id, name, location)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False


# ==================== TELEMETRY FUNCTIONS ====================

def save_telemetry(device_id: int, temperature: float, humidity: float = None,
                   alarm_state: bool = False, cooler_state: bool = False,
                   gateway_id: int = None, node_timestamp: int = None,
                   gateway_timestamp: int = None, measured_at: str = None):
    """Lưu dữ liệu telemetry"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO telemetry 
            (device_id, gateway_id, temperature, humidity, alarm_state, cooler_state,
             node_timestamp, gateway_timestamp, measured_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (device_id, gateway_id, temperature, humidity, alarm_state, cooler_state,
              node_timestamp, gateway_timestamp, measured_at))
        conn.commit()
        conn.close()
        print(f"[DB] Saved telemetry: device={device_id}, temp={temperature}°C")


def save_batch_telemetry(gateway_id: int, data_list: List[Dict]):
    """Lưu batch dữ liệu telemetry (50 mẫu/lần)"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        
        count = 0
        for item in data_list:
            # Tính toán thời gian đo thực tế từ timestamp
            measured_at = datetime.now().isoformat()
            if 'gateway_timestamp' in item:
                # Có thể convert timestamp sang thời gian thực
                pass
            
            cursor.execute("""
                INSERT INTO telemetry 
                (device_id, gateway_id, temperature, humidity, alarm_state, cooler_state,
                 node_timestamp, gateway_timestamp, measured_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get('device_id', 0),
                gateway_id,
                item.get('temperature', 0),
                item.get('humidity'),
                item.get('alarm_state', False),
                item.get('cooler_state', False),
                item.get('node_timestamp'),
                item.get('gateway_timestamp'),
                measured_at
            ))
            count += 1
        
        conn.commit()
        conn.close()
        print(f"[DB] Saved batch: {count} records from gateway {gateway_id}")
        return count


def get_recent_telemetry(device_id: int = None, limit: int = 100) -> List[Dict]:
    """Lấy dữ liệu telemetry gần đây"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        
        if device_id:
            cursor.execute("""
                SELECT * FROM telemetry 
                WHERE device_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """, (device_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM telemetry 
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def get_telemetry_stats(device_id: int) -> Dict:
    """Thống kê nhiệt độ của thiết bị"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                AVG(temperature) as avg_temp,
                MIN(temperature) as min_temp,
                MAX(temperature) as max_temp,
                AVG(humidity) as avg_humidity
            FROM telemetry 
            WHERE device_id = ?
        """, (device_id,))
        row = cursor.fetchone()
        conn.close()
        
        return {
            "device_id": device_id,
            "total_records": row[0],
            "avg_temp": round(row[1], 2) if row[1] else None,
            "min_temp": row[2],
            "max_temp": row[3],
            "avg_humidity": round(row[4], 2) if row[4] else None
        }


def get_latest_telemetry(device_id: int) -> Optional[Dict]:
    """Lấy dữ liệu mới nhất của thiết bị"""
    data = get_recent_telemetry(device_id=device_id, limit=1)
    return data[0] if data else None


# ==================== ALERT FUNCTIONS ====================

def create_alert(device_id: int, alert_type: str, temperature: float = None, 
                 message: str = None):
    """Tạo cảnh báo mới"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alerts (device_id, alert_type, temperature, message)
            VALUES (?, ?, ?, ?)
        """, (device_id, alert_type, temperature, message))
        conn.commit()
        alert_id = cursor.lastrowid
        conn.close()
        print(f"[DB] Alert created: {alert_type} for device {device_id}")
        return alert_id


def get_active_alerts() -> List[Dict]:
    """Lấy danh sách cảnh báo chưa xác nhận"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, d.name as device_name, d.location
            FROM alerts a
            LEFT JOIN devices d ON a.device_id = d.device_id
            WHERE a.acknowledged = 0
            ORDER BY a.created_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]


def acknowledge_alert(alert_id: int) -> bool:
    """Xác nhận đã xử lý cảnh báo"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alerts 
            SET acknowledged = 1, acknowledged_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (alert_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0


# ==================== COMMAND FUNCTIONS ====================

def save_command(device_id: int, command: str, gateway_id: int = None) -> int:
    """Lưu lệnh điều khiển"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO commands (device_id, gateway_id, command)
            VALUES (?, ?, ?)
        """, (device_id, gateway_id, command))
        conn.commit()
        cmd_id = cursor.lastrowid
        conn.close()
        print(f"[DB] Command saved: {command} for device {device_id}")
        return cmd_id


def update_command_status(cmd_id: int, status: str, response: str = None):
    """Cập nhật trạng thái lệnh"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE commands 
            SET status = ?, response = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, response, cmd_id))
        conn.commit()
        conn.close()


def get_command_history(device_id: int = None, limit: int = 50) -> List[Dict]:
    """Lấy lịch sử lệnh"""
    with _lock:
        conn = get_connection()
        cursor = conn.cursor()
        
        if device_id:
            cursor.execute("""
                SELECT * FROM commands 
                WHERE device_id = ?
                ORDER BY created_at DESC LIMIT ?
            """, (device_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM commands 
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
