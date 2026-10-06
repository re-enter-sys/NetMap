"""
NetMap - Historical intelligence.
"""

from netmap.database import (
    get_connection,
    list_topology_history,
)


def device_history(
    ip: str,
) -> list[dict]:
    """Return historical information for an IP."""

    connection = get_connection()

    device = connection.execute(
        """
        SELECT *
        FROM devices
        WHERE ip = ?
        """,
        (ip,),
    ).fetchone()

    if not device:
        connection.close()
        return []

    services = connection.execute(
        """
        SELECT *
        FROM services
        WHERE device_id = ?
        ORDER BY port
        """,
        (device["id"],),
    ).fetchall()

    events = connection.execute(
        """
        SELECT *
        FROM events
        WHERE ip = ?
        ORDER BY timestamp DESC
        LIMIT 100
        """,
        (ip,),
    ).fetchall()

    alerts = connection.execute(
        """
        SELECT *
        FROM alerts
        WHERE ip = ?
        ORDER BY timestamp DESC
        LIMIT 100
        """,
        (ip,),
    ).fetchall()

    connection.close()

    result = dict(device)

    result["services"] = [
        dict(service)
        for service in services
    ]

    result["events"] = [
        dict(event)
        for event in events
    ]

    result["alerts"] = [
        dict(alert)
        for alert in alerts
    ]

    return [result]


def topology_history(
    limit: int = 50,
) -> list[dict]:
    """Return historical topology snapshots."""

    return list_topology_history(
        limit=limit
    )


def latest_device_inventory() -> list[dict]:
    """Return the latest device inventory."""

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
