"""
NetMap - Advanced device fingerprinting.

Combines network discovery information with:
- MAC/vendor information
- hostname
- open ports
- detected services
- operating system
- device type
"""

from typing import Any


def infer_device_type(device: dict[str, Any]) -> str:
    """Infer a basic device category from discovered information."""

    hostname = (
        device.get("hostname") or ""
    ).lower()

    vendor = (
        device.get("vendor") or ""
    ).lower()

    services = device.get(
        "services",
        [],
    )

    ports = {
        service.get("port")
        for service in services
    }

    if any(
        value in hostname
        for value in (
            "router",
            "gateway",
            "firewall",
        )
    ):
        return "Network Appliance"

    if 3389 in ports:
        return "Windows Host"

    if 22 in ports:
        return "Linux/Unix Host"

    if 445 in ports:
        return "Windows/SMB Host"

    if 80 in ports or 443 in ports:
        return "Web Server"

    if "vmware" in vendor:
        return "Virtualization Device"

    return "Unknown Device"


def fingerprint_device(
    device: dict[str, Any],
) -> dict[str, Any]:
    """Create an enriched device fingerprint."""

    result = dict(device)

    result.setdefault(
        "services",
        [],
    )

    result.setdefault(
        "os",
        None,
    )

    result.setdefault(
        "os_confidence",
        None,
    )

    result["device_type"] = infer_device_type(
        result
    )

    return result
