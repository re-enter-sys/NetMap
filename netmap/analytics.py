"""
NetMap - Security analytics.
"""

from netmap.database import get_connection
from netmap.risk import calculate_network_risk


def dashboard_analytics() -> dict:
    """Return dashboard-ready security statistics."""

    connection = get_connection()

    device_count = connection.execute(
        "SELECT COUNT(*) FROM devices"
    ).fetchone()[0]

    service_count = connection.execute(
        "SELECT COUNT(*) FROM services"
    ).fetchone()[0]

    event_count = connection.execute(
        "SELECT COUNT(*) FROM events"
    ).fetchone()[0]

    open_alerts = connection.execute(
        """
        SELECT COUNT(*)
        FROM alerts
        WHERE status = 'OPEN'
        """
    ).fetchone()[0]

    acknowledged = connection.execute(
        """
        SELECT COUNT(*)
        FROM alerts
        WHERE status = 'ACKNOWLEDGED'
        """
    ).fetchone()[0]

    resolved = connection.execute(
        """
        SELECT COUNT(*)
        FROM alerts
        WHERE status = 'RESOLVED'
        """
    ).fetchone()[0]

    severity_rows = connection.execute(
        """
        SELECT severity, COUNT(*) AS count
        FROM alerts
        GROUP BY severity
        ORDER BY count DESC
        """
    ).fetchall()

    severity = {
        row["severity"]: row["count"]
        for row in severity_rows
    }

    service_rows = connection.execute(
        """
        SELECT
            service,
            COUNT(*) AS count
        FROM services
        WHERE service IS NOT NULL
        GROUP BY service
        ORDER BY count DESC
        LIMIT 10
        """
    ).fetchall()

    services = {
        row["service"]: row["count"]
        for row in service_rows
    }

    role_rows = connection.execute(
        """
        SELECT
            role,
            COUNT(*) AS count
        FROM devices
        GROUP BY role
        ORDER BY count DESC
        """
    ).fetchall()

    roles = {
        row["role"] or "Unknown": row["count"]
        for row in role_rows
    }

    os_rows = connection.execute(
        """
        SELECT
            os,
            COUNT(*) AS count
        FROM devices
        GROUP BY os
        ORDER BY count DESC
        """
    ).fetchall()

    operating_systems = {
        row["os"] or "Unknown": row["count"]
        for row in os_rows
    }

    devices = [
        dict(row)
        for row in connection.execute(
            """
            SELECT *
            FROM devices
            """
        ).fetchall()
    ]

    connection.close()

    risk = calculate_network_risk(
        devices
    )

    return {
        "devices": device_count,

        "services": service_count,

        "events": event_count,

        "alerts": {
            "open": open_alerts,
            "acknowledged": acknowledged,
            "resolved": resolved,
            "total":
                open_alerts
                + acknowledged
                + resolved,
        },

        "severity": severity,

        "services_breakdown": services,

        "roles": roles,

        "operating_systems":
            operating_systems,

        "risk": risk,
    }
