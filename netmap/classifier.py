"""
NetMap - Device classification.
"""

from typing import Any


def classify_device(
    device: dict[str, Any],
    local_ip: str,
    gateway_ip: str | None,
) -> str:
    """
    Assign a basic role to a discovered device.
    """

    ip_address = device.get("ip")

    if ip_address == local_ip:
        return "Local Host"

    if gateway_ip and ip_address == gateway_ip:
        return "Gateway"

    return "Device"
