"""
NetMap - Live network monitoring.

Compares consecutive network scans and detects
devices appearing or disappearing.
"""

from typing import Any


def device_key(device: dict[str, Any]) -> str:
    """
    Return a stable identifier for a network device.

    IP address is used as the primary identifier because
    every discovered device should have an IPv4 address.
    """

    return device["ip"]


def compare_devices(
    previous: list[dict[str, Any]],
    current: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """
    Compare two device lists.

    Returns:
        A dictionary containing:
        - added: devices found only in current scan
        - removed: devices found only in previous scan
        - unchanged: devices present in both scans
    """

    previous_map = {
        device_key(device): device
        for device in previous
    }

    current_map = {
        device_key(device): device
        for device in current
    }

    previous_ips = set(previous_map)
    current_ips = set(current_map)

    added_ips = current_ips - previous_ips
    removed_ips = previous_ips - current_ips
    unchanged_ips = current_ips & previous_ips

    return {
        "added": [
            current_map[ip]
            for ip in sorted(added_ips)
        ],
        "removed": [
            previous_map[ip]
            for ip in sorted(removed_ips)
        ],
        "unchanged": [
            current_map[ip]
            for ip in sorted(unchanged_ips)
        ],
    }
