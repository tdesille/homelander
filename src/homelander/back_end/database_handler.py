import sqlite3
from homelander.utils.schemas import ControllableDeviceInfos
from homelander.utils.constants import DB_PATH, TABLE_NAME
from typing import List
import logging

logger = logging.getLogger(__name__)

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    logger.debug(f"Connected to database at {DB_PATH}")
    return (conn, conn.cursor())

def commit_db(conn : sqlite3.Connection) :
    conn.commit()
    logger.debug("Changes committed to database")
    return

def close_db(conn : sqlite3.Connection) :
    conn.close()
    logger.debug("Database connection closed")
    return

def get_devices() -> List[ControllableDeviceInfos] :
    conn, cursor = connect_db()
    cursor.execute(f"SELECT friendly_name, ieee_name FROM {TABLE_NAME} WHERE status = 'ACTIVE'")
    rows = cursor.fetchall()
    close_db(conn)
    devices = [ControllableDeviceInfos(friendly_name=row[0], ieee_name=row[1]) for row in rows]
    logger.debug(f"Retrieved devices from database: {devices}")
    return devices

def insert_new_devices(cursor: sqlite3.Cursor, new_devices: List[ControllableDeviceInfos]):
    rows = [(d.friendly_name, d.ieee_name, d.friendly_name) for d in new_devices]
    logger.debug(f"Inserting new devices (duplicates will be skipped): {rows}")
    cursor.executemany(
        """INSERT OR IGNORE INTO devices (friendly_name, ieee_name, display_name, status, power_state)
           VALUES (?, ?, ?, 'ACTIVE', 0)""",
        rows
    )

def deactivate_missing_devices(cursor: sqlite3.Cursor, active_devices: List[ControllableDeviceInfos]):
    ieee_names = [d.ieee_name for d in active_devices]
    logger.debug(f"Deactivating devices not in: {ieee_names}")
    cursor.execute(
        f"UPDATE devices SET status = 'INACTIVE' WHERE ieee_name NOT IN ({','.join('?'*len(ieee_names))})",
        ieee_names
    )

def sync_db_with_new_devices(new_devices: List[ControllableDeviceInfos]):
    conn, cursor = connect_db()
    insert_new_devices(cursor, new_devices)
    commit_db(conn)
    deactivate_missing_devices(cursor, new_devices)
    commit_db(conn)
    close_db(conn)
    logger.info("Database synchronized with new device list")
    return
