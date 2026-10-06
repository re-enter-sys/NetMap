"""
NetMap - Active network device discovery.

Uses Nmap host discovery to identify active devices
on the local authorized network.
"""

import re
import subprocess
from typing import Any


def scan_network(network: str) -> list[dict[str, Any]]:
    """
    Discover active devices on a network using Nmap.

    Args:
        network: IPv4 network in CIDR notation.

    Returns:
        A list of discovered devices.
    """

    command = [
        "nmap",
        "-sn",
        network,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Nmap scan failed: {result.stderr.strip()}"
        )

    devices = []

    current_device: dict[str, Any] | None = None

    for line in result.stdout.splitlines():

        line = line.strip()

        if line.startswith("Nmap scan report for "):

            if current_device:
                devices.append(current_device)

            target = line.replace(
                "Nmap scan report for ",
                "",
                1,
            )

            hostname = None
            ip_address = target

            match = re.match(
                r"(.+?)\s+\((\d+\.\d+\.\d+\.\d+)\)$",
                target,
            )

            if match:
                hostname = match.group(1)
                ip_address = match.group(2)

            current_device = {
                "ip": ip_address,
                "hostname": hostname,
                "mac": None,
                "vendor": None,
                "status": "up",
            }

        elif line.startswith("MAC Address:") and current_device:

            mac_match = re.search(
                r"MAC Address:\s+([0-9A-Fa-f:]{17})(?:\s+\((.*?)\))?$",
                line,
            )

            if mac_match:
                current_device["mac"] = mac_match.group(1)
                current_device["vendor"] = mac_match.group(2)

    if current_device:
        devices.append(current_device)

    return devices
