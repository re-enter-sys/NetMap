"""
NetMap - Network anomaly detection.
"""

from typing import Any


def detect_anomalies(
    previous: list[dict[str, Any]],
    current: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Detect meaningful changes between network states."""

    previous_map = {
        item["ip"]: item
        for item in previous
    }

    current_map = {
        item["ip"]: item
        for item in current
    }

    anomalies = []

    for ip, device in current_map.items():

        if ip not in previous_map:

            anomalies.append(
                {
                    "type": "NEW_DEVICE",
                    "severity": "MEDIUM",
                    "ip": ip,
                    "message": (
                        f"New device detected: {ip}"
                    ),
                }
            )

            continue

        old = previous_map[ip]

        old_mac = old.get("mac")
        new_mac = device.get("mac")

        if (
            old_mac
            and new_mac
            and old_mac != new_mac
        ):

            anomalies.append(
                {
                    "type": "MAC_CHANGE",
                    "severity": "HIGH",
                    "ip": ip,
                    "message": (
                        f"MAC address changed "
                        f"for {ip}"
                    ),
                }
            )

        old_services = {
            service.get("port")
            for service in old.get(
                "services",
                [],
            )
        }

        new_services = {
            service.get("port")
            for service in device.get(
                "services",
                [],
            )
        }

        for port in new_services - old_services:

            anomalies.append(
                {
                    "type": "NEW_PORT",
                    "severity": "HIGH",
                    "ip": ip,
                    "port": port,
                    "message": (
                        f"New port {port} "
                        f"detected on {ip}"
                    ),
                }
            )

        for port in old_services - new_services:

            anomalies.append(
                {
                    "type": "PORT_CLOSED",
                    "severity": "LOW",
                    "ip": ip,
                    "port": port,
                    "message": (
                        f"Port {port} "
                        f"closed on {ip}"
                    ),
                }
            )

        old_os = old.get("os")
        new_os = device.get("os")

        if (
            old_os
            and new_os
            and old_os != new_os
        ):

            anomalies.append(
                {
                    "type": "OS_CHANGE",
                    "severity": "HIGH",
                    "ip": ip,
                    "message": (
                        f"OS fingerprint changed "
                        f"for {ip}"
                    ),
                }
            )

    return anomalies
