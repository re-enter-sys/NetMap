"""
NetMap - SQLite persistence layer.

Stores:
    - Devices
    - Services
    - Events
    - Security alerts
    - Topology history
    - Baseline snapshots

The database is intentionally self-contained so the live monitor
and dashboard can share the same persistence layer.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


DATABASE_PATH = Path("reports/netmap.db")


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------

def init_database() -> None:
    """Create NetMap database tables."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            hostname TEXT,
            mac TEXT,
            vendor TEXT,
            role TEXT,
            device_type TEXT,
            os TEXT,
            os_confidence INTEGER,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            times_seen INTEGER DEFAULT 1
        );

        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_devices_ip
        ON devices(ip);


        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER NOT NULL,
            port INTEGER NOT NULL,
            protocol TEXT,
            service TEXT,
            version TEXT,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,

            UNIQUE(
                device_id,
                port,
                protocol
            ),

            FOREIGN KEY(device_id)
                REFERENCES devices(id)
                ON DELETE CASCADE
        );


        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            severity TEXT,
            ip TEXT,
            message TEXT,
            data TEXT
        );


        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            title TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN',
            message TEXT,
            ip TEXT,
            device TEXT,
            acknowledged_by TEXT,
            acknowledged_at TEXT,
            resolved_at TEXT,
            data TEXT
        );


        CREATE TABLE IF NOT EXISTS topology_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            topology TEXT NOT NULL
        );


        CREATE TABLE IF NOT EXISTS baselines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            snapshot TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )

    connection.commit()
    connection.close()


# ---------------------------------------------------------------------------
# Devices
# ---------------------------------------------------------------------------

def upsert_device(
    device: dict[str, Any],
) -> int:
    """Insert or update a device."""

    timestamp = (
        device.get("last_seen")
        or device.get("timestamp")
        or datetime.now().isoformat()
    )

    connection = get_connection()

    cursor = connection.cursor()

    existing = cursor.execute(
        """
        SELECT id
        FROM devices
        WHERE ip = ?
        """,
        (
            device["ip"],
        ),
    ).fetchone()

    if existing:

        cursor.execute(
            """
            UPDATE devices
            SET hostname = ?,
                mac = ?,
                vendor = ?,
                role = ?,
                device_type = ?,
                os = ?,
                os_confidence = ?,
                last_seen = ?,
                times_seen = times_seen + 1
            WHERE id = ?
            """,
            (
                device.get("hostname"),
                device.get("mac"),
                device.get("vendor"),
                device.get("role"),
                device.get("device_type"),
                device.get("os"),
                device.get("os_confidence"),
                timestamp,
                existing["id"],
            ),
        )

        device_id = existing["id"]

    else:

        cursor.execute(
            """
            INSERT INTO devices (
                ip,
                hostname,
                mac,
                vendor,
                role,
                device_type,
                os,
                os_confidence,
                first_seen,
                last_seen
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                device["ip"],
                device.get("hostname"),
                device.get("mac"),
                device.get("vendor"),
                device.get("role"),
                device.get("device_type"),
                device.get("os"),
                device.get("os_confidence"),
                timestamp,
                timestamp,
            ),
        )

        device_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return int(device_id)


def list_devices() -> list[dict]:
    """Return historical devices."""

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM devices
        ORDER BY last_seen DESC
        """
    ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


def get_device(
    device_id: int,
) -> dict | None:
    """Return one historical device."""

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM devices
        WHERE id = ?
        """,
        (
            device_id,
        ),
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

def save_services(
    device_id: int,
    services: list[dict[str, Any]],
    timestamp: str | None = None,
) -> None:
    """Persist discovered services."""

    timestamp = (
        timestamp
        or datetime.now().isoformat()
    )

    connection = get_connection()

    cursor = connection.cursor()

    for service in services:

        cursor.execute(
            """
            INSERT INTO services (
                device_id,
                port,
                protocol,
                service,
                version,
                first_seen,
                last_seen
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(
                device_id,
                port,
                protocol
            )
            DO UPDATE SET
                service = excluded.service,
                version = excluded.version,
                last_seen = excluded.last_seen
            """,
            (
                device_id,
                service["port"],
                service.get(
                    "protocol",
                    "tcp",
                ),
                service.get("service"),
                service.get("version"),
                timestamp,
                timestamp,
            ),
        )

    connection.commit()
    connection.close()


def list_services(
    device_id: int | None = None,
) -> list[dict]:
    """Return discovered services."""

    connection = get_connection()

    if device_id is None:

        rows = connection.execute(
            """
            SELECT
                services.*,
                devices.ip,
                devices.hostname
            FROM services
            JOIN devices
                ON devices.id = services.device_id
            ORDER BY
                services.last_seen DESC,
                services.port ASC
            """
        ).fetchall()

    else:

        rows = connection.execute(
            """
            SELECT
                services.*,
                devices.ip,
                devices.hostname
            FROM services
            JOIN devices
                ON devices.id = services.device_id
            WHERE services.device_id = ?
            ORDER BY services.port ASC
            """,
            (
                device_id,
            ),
        ).fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def save_event(
    *args,
    **kwargs,
) -> None:
    """
    Persist an event.

    Supported forms:

    Modern:
        save_event(
            event_type,
            severity,
            ip,
            message,
            data=None,
        )

    Compatibility form:
        save_event(
            timestamp,
            event_type,
            severity,
            ip,
            message,
            data,
        )
    """

    timestamp = kwargs.pop(
        "timestamp",
        None,
    )

    event_type = kwargs.pop(
        "event_type",
        None,
    )

    severity = kwargs.pop(
        "severity",
        None,
    )

    ip = kwargs.pop(
        "ip",
        None,
    )

    message = kwargs.pop(
        "message",
        None,
    )

    data = kwargs.pop(
        "data",
        None,
    )

    if args:

        if len(args) == 5:
            (
                event_type,
                severity,
                ip,
                message,
                data,
            ) = args

        elif len(args) == 6:
            (
                timestamp,
                event_type,
                severity,
                ip,
                message,
                data,
            ) = args

        else:
            raise TypeError(
                "save_event() expects 5 or 6 positional arguments"
            )

    timestamp = (
        timestamp
        or datetime.now().isoformat()
    )

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO events (
            timestamp,
            event_type,
            severity,
            ip,
            message,
            data
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            event_type,
            severity,
            ip,
            message,
            json.dumps(
                data or {}
            ),
        ),
    )

    connection.commit()
    connection.close()


def list_events(
    limit: int = 500,
    severity: str | None = None,
    event_type: str | None = None,
) -> list[dict]:
    """Return historical events with optional filters."""

    connection = get_connection()

    query = """
        SELECT *
        FROM events
        WHERE 1 = 1
    """

    params: list[Any] = []

    if severity:
        query += " AND severity = ?"
        params.append(severity)

    if event_type:
        query += " AND event_type = ?"
        params.append(event_type)

    query += """
        ORDER BY timestamp DESC
        LIMIT ?
    """

    params.append(int(limit))

    rows = connection.execute(
        query,
        params,
    ).fetchall()

    connection.close()

    results = []

    for row in rows:

        item = dict(row)

        try:
            item["data"] = json.loads(
                item.get("data") or "{}"
            )
        except json.JSONDecodeError:
            item["data"] = {}

        results.append(item)

    return results


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------

def save_alert(
    alert: dict[str, Any] | None = None,
    **kwargs,
) -> int:
    """
    Persist a security alert.

    Accepts either a dictionary or keyword arguments.
    """

    alert = dict(
        alert or {}
    )

    alert.update(kwargs)

    timestamp = (
        alert.get("timestamp")
        or datetime.now().isoformat()
    )

    alert_type = (
        alert.get("alert_type")
        or alert.get("type")
        or "UNKNOWN"
    )

    title = (
        alert.get("title")
        or alert.get("message")
        or "NetMap Security Alert"
    )

    severity = (
        alert.get("severity")
        or "INFO"
    )

    status = (
        alert.get("status")
        or "OPEN"
    )

    message = alert.get(
        "message"
    )

    ip = alert.get(
        "ip"
    )

    device = (
        alert.get("device")
        or alert.get("hostname")
    )

    acknowledged_by = alert.get(
        "acknowledged_by"
    )

    acknowledged_at = alert.get(
        "acknowledged_at"
    )

    resolved_at = alert.get(
        "resolved_at"
    )

    reserved_keys = {
        "timestamp",
        "alert_type",
        "type",
        "title",
        "severity",
        "status",
        "message",
        "ip",
        "device",
        "hostname",
        "acknowledged_by",
        "acknowledged_at",
        "resolved_at",
        "data",
    }

    extra_data = alert.get(
        "data"
    )

    if extra_data is None:

        extra_data = {
            key: value
            for key, value in alert.items()
            if key not in reserved_keys
        }

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO alerts (
            timestamp,
            alert_type,
            title,
            severity,
            status,
            message,
            ip,
            device,
            acknowledged_by,
            acknowledged_at,
            resolved_at,
            data
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            alert_type,
            title,
            severity,
            status,
            message,
            ip,
            device,
            acknowledged_by,
            acknowledged_at,
            resolved_at,
            json.dumps(
                extra_data or {}
            ),
        ),
    )

    alert_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return int(alert_id)


def list_alerts(
    status: str | None = None,
    severity: str | None = None,
    alert_type: str | None = None,
    limit: int = 500,
) -> list[dict]:
    """Return alerts with optional filters."""

    connection = get_connection()

    query = """
        SELECT *
        FROM alerts
        WHERE 1 = 1
    """

    params: list[Any] = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if severity:
        query += " AND severity = ?"
        params.append(severity)

    if alert_type:
        query += " AND alert_type = ?"
        params.append(alert_type)

    query += """
        ORDER BY timestamp DESC
        LIMIT ?
    """

    params.append(int(limit))

    rows = connection.execute(
        query,
        params,
    ).fetchall()

    connection.close()

    results = []

    for row in rows:

        item = dict(row)

        try:
            item["data"] = json.loads(
                item.get("data") or "{}"
            )
        except json.JSONDecodeError:
            item["data"] = {}

        results.append(item)

    return results


def acknowledge_alert(
    alert_id: int,
    acknowledged_by: str = "admin",
) -> bool:
    """Acknowledge an open security alert."""

    timestamp = datetime.now().isoformat()

    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE alerts
        SET status = 'ACKNOWLEDGED',
            acknowledged_by = ?,
            acknowledged_at = ?
        WHERE id = ?
          AND status = 'OPEN'
        """,
        (
            acknowledged_by,
            timestamp,
            alert_id,
        ),
    )

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


def resolve_alert(
    alert_id: int,
) -> bool:
    """Resolve a security alert."""

    timestamp = datetime.now().isoformat()

    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE alerts
        SET status = 'RESOLVED',
            resolved_at = ?
        WHERE id = ?
          AND status != 'RESOLVED'
        """,
        (
            timestamp,
            alert_id,
        ),
    )

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


# ---------------------------------------------------------------------------
# Topology history
# ---------------------------------------------------------------------------

def save_topology(
    topology: dict[str, Any],
) -> None:
    """Persist a topology snapshot."""

    timestamp = datetime.now().isoformat()

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO topology_snapshots (
            timestamp,
            topology
        )
        VALUES (?, ?)
        """,
        (
            timestamp,
            json.dumps(
                topology
            ),
        ),
    )

    connection.commit()
    connection.close()


def list_topology_history(
    limit: int = 100,
) -> list[dict]:
    """Return historical topology snapshots."""

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT id, timestamp, topology
        FROM topology_snapshots
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (
            int(limit),
        ),
    ).fetchall()

    connection.close()

    results = []

    for row in rows:

        item = dict(row)

        try:
            item["topology"] = json.loads(
                item["topology"]
            )
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            item["topology"] = {}

        results.append(item)

    return results


def get_latest_topology() -> dict | None:
    """Return the latest topology snapshot."""

    history = list_topology_history(
        limit=1
    )

    if not history:
        return None

    return history[0]


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------

def save_baseline(
    ip: str,
    snapshot: dict[str, Any],
) -> int:
    """Save a device baseline snapshot."""

    timestamp = datetime.now().isoformat()

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO baselines (
            ip,
            snapshot,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            ip,
            json.dumps(snapshot),
            timestamp,
        ),
    )

    baseline_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return int(baseline_id)


def list_baselines(
    ip: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Return stored device baselines."""

    connection = get_connection()

    if ip:

        rows = connection.execute(
            """
            SELECT *
            FROM baselines
            WHERE ip = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                ip,
                int(limit),
            ),
        ).fetchall()

    else:

        rows = connection.execute(
            """
            SELECT *
            FROM baselines
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (
                int(limit),
            ),
        ).fetchall()

    connection.close()

    results = []

    for row in rows:

        item = dict(row)

        try:
            item["snapshot"] = json.loads(
                item["snapshot"]
            )
        except (
            json.JSONDecodeError,
            TypeError,
        ):
            item["snapshot"] = {}

        results.append(item)

    return results


# ---------------------------------------------------------------------------
# Startup initialization
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_database()
    print(
        f"NetMap database initialized: {DATABASE_PATH}"
    )
