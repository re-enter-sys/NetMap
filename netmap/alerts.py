"""
NetMap - Security alert engine and alert management.

The alert engine creates security alerts while the database
module handles SQLite persistence.
"""

from datetime import datetime
from typing import Any

from netmap.database import (
    acknowledge_alert as database_acknowledge_alert,
    list_alerts as database_list_alerts,
    resolve_alert as database_resolve_alert,
    save_alert as database_save_alert,
)


SEVERITY_ORDER = {
    "INFO": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


# ============================================================================
# Alert creation
# ============================================================================

def create_device_alert(
    device: dict[str, Any],
    event_type: str,
) -> dict[str, Any]:
    """Create a structured security alert for a device event."""

    ip = device.get(
        "ip",
        "Unknown",
    )

    hostname = (
        device.get("hostname")
        or "Unknown"
    )

    mac = (
        device.get("mac")
        or "Unknown"
    )

    role = device.get(
        "role",
        "Device",
    )

    vendor = device.get(
        "vendor",
        "Unknown",
    )

    if event_type == "NEW_DEVICE":

        severity = "MEDIUM"

        title = (
            "New Network Device Detected"
        )

        alert_type = (
            "NETWORK_DEVICE_CHANGE"
        )

        message = (
            f"New device detected at {ip}"
        )

    elif event_type == "DEVICE_REMOVED":

        severity = "LOW"

        title = (
            "Network Device Removed"
        )

        alert_type = (
            "NETWORK_DEVICE_REMOVED"
        )

        message = (
            f"Previously detected device "
            f"went offline: {ip}"
        )

    elif event_type == "NEW_PORT":

        severity = "HIGH"

        title = (
            "New Network Service Detected"
        )

        alert_type = (
            "NEW_NETWORK_SERVICE"
        )

        message = (
            f"New service detected on {ip}"
        )

    elif event_type == "ANOMALY":

        severity = "HIGH"

        title = (
            "Network Anomaly Detected"
        )

        alert_type = (
            "NETWORK_ANOMALY"
        )

        message = (
            f"Network anomaly detected for {ip}"
        )

    else:

        severity = "INFO"

        title = "Network Event"

        alert_type = (
            "NETWORK_EVENT"
        )

        message = (
            f"Network event detected "
            f"for {ip}"
        )

    return {
        "timestamp":
            datetime.now().isoformat(),

        # Keep the original "type" field because
        # live.py currently uses it.
        "type":
            alert_type,

        # Also expose alert_type for the new
        # database/dashboard API.
        "alert_type":
            alert_type,

        "title":
            title,

        "severity":
            severity,

        "status":
            "OPEN",

        "message":
            message,

        "ip":
            ip,

        "device":
            {
                "ip":
                    ip,

                "hostname":
                    hostname,

                "mac":
                    mac,

                "role":
                    role,

                "vendor":
                    vendor,
            },

        "data":
            {
                "event_type":
                    event_type,

                "device":
                    {
                        "ip":
                            ip,

                        "hostname":
                            hostname,

                        "mac":
                            mac,

                        "role":
                            role,

                        "vendor":
                            vendor,
                    },
            },
    }


# ============================================================================
# Alert persistence
# ============================================================================

def save_alert(
    alert: dict[str, Any],
) -> int:
    """
    Persist an alert through the central database layer.

    The function keeps the original live.py interface intact.
    """

    device = alert.get(
        "device",
        {},
    )

    payload = {
        "timestamp":
            alert.get(
                "timestamp"
            ),

        "alert_type":
            alert.get(
                "alert_type"
            )
            or alert.get(
                "type",
                "UNKNOWN",
            ),

        "title":
            alert.get(
                "title",
                "NetMap Security Alert",
            ),

        "severity":
            alert.get(
                "severity",
                "INFO",
            ),

        "status":
            alert.get(
                "status",
                "OPEN",
            ),

        "message":
            alert.get(
                "message",
                "",
            ),

        "ip":
            alert.get(
                "ip"
            )
            or device.get(
                "ip"
            ),

        "device":
            device.get(
                "hostname"
            )
            or alert.get(
                "hostname"
            ),

        "data":
            alert.get(
                "data",
                {},
            ),
    }

    return database_save_alert(
        payload
    )


# ============================================================================
# Alert retrieval
# ============================================================================

def list_alerts(
    status: str | None = None,
    severity: str | None = None,
    alert_type: str | None = None,
    limit: int = 500,
) -> list[dict]:
    """Return alerts with optional filters."""

    return database_list_alerts(
        status=status,
        severity=severity,
        alert_type=alert_type,
        limit=limit,
    )


# ============================================================================
# Alert acknowledgement
# ============================================================================

def acknowledge_alert(
    alert_id: int,
    username: str,
) -> bool:
    """Acknowledge an alert."""

    return database_acknowledge_alert(
        alert_id,
        username,
    )


# ============================================================================
# Alert resolution
# ============================================================================

def resolve_alert(
    alert_id: int,
) -> bool:
    """Resolve an alert."""

    return database_resolve_alert(
        alert_id,
    )


# ============================================================================
# Severity helpers
# ============================================================================

def severity_value(
    severity: str,
) -> int:
    """Return numeric severity value."""

    return SEVERITY_ORDER.get(
        severity.upper(),
        0,
    )


def severity_at_least(
    severity: str,
    minimum: str,
) -> bool:
    """Check whether severity meets a minimum threshold."""

    return (
        severity_value(
            severity
        )
        >=
        severity_value(
            minimum
        )
    )


# ============================================================================
# CLI self-test
# ============================================================================

if __name__ == "__main__":

    test_device = {
        "ip": "10.10.10.250",
        "hostname": "test-device",
        "mac": "00:11:22:33:44:55",
        "role": "Device",
        "vendor": "Test Vendor",
    }

    alert = create_device_alert(
        test_device,
        "NEW_DEVICE",
    )

    print(
        "Generated alert:"
    )

    print(alert)
