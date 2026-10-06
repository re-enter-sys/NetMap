"""
NetMap - Security alert engine.

Converts network device changes into
structured security alerts.
"""

from datetime import datetime
from typing import Any


def create_device_alert(
    device: dict[str, Any],
    event_type: str,
) -> dict[str, Any]:
    """
    Create a security alert for a network device change.
    """

    ip_address = device.get(
        "ip",
        "Unknown",
    )

    hostname = device.get(
        "hostname"
    ) or "Unknown"

    mac = device.get(
        "mac"
    ) or "Unknown"


    if event_type == "NEW_DEVICE":

        severity = "MEDIUM"

        title = "New Network Device Detected"

        alert_type = (
            "NETWORK_DEVICE_CHANGE"
        )

        message = (
            f"New device detected at "
            f"{ip_address}"
        )

    elif event_type == "DEVICE_REMOVED":

        severity = "LOW"

        title = "Network Device Removed"

        alert_type = (
            "NETWORK_DEVICE_REMOVED"
        )

        message = (
            f"Previously detected device "
            f"went offline: {ip_address}"
        )

    else:

        severity = "INFO"

        title = "Network Device Event"

        alert_type = "NETWORK_EVENT"

        message = (
            f"Network event detected "
            f"for {ip_address}"
        )


    return {
        "timestamp":
            datetime.now().isoformat(),

        "type":
            alert_type,

        "title":
            title,

        "severity":
            severity,

        "message":
            message,

        "device": {
            "ip":
                ip_address,

            "hostname":
                hostname,

            "mac":
                mac,

            "role":
                device.get(
                    "role",
                    "Device",
                ),

            "vendor":
                device.get(
                    "vendor",
                    "Unknown",
                ),
        },
    }
