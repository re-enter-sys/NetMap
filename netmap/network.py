"""
NetMap - Network interface discovery.

Collects local IPv4 network interface information including:
- Interface name
- IPv4 address
- Netmask
- CIDR network
- MAC address
"""

import ipaddress
import socket
from typing import Any

import psutil


def get_interfaces() -> list[dict[str, Any]]:
    """
    Discover usable IPv4 network interfaces.

    Loopback interfaces are excluded because they do not
    represent an external/local network segment.

    Returns:
        A list of dictionaries containing interface information.
    """

    interfaces = []

    for interface_name, addresses in psutil.net_if_addrs().items():

        # Ignore loopback.
        if interface_name == "lo":
            continue

        ipv4_address = None
        netmask = None
        mac_address = None

        for address in addresses:

            if address.family == socket.AF_INET:
                ipv4_address = address.address
                netmask = address.netmask

            elif address.family == psutil.AF_LINK:
                mac_address = address.address

        if not ipv4_address or not netmask:
            continue

        # Ignore loopback IPv4 addresses.
        if ipv4_address.startswith("127."):
            continue

        try:
            network = ipaddress.IPv4Network(
                f"{ipv4_address}/{netmask}",
                strict=False,
            )
        except ValueError:
            continue

        interfaces.append(
            {
                "interface": interface_name,
                "ip": ipv4_address,
                "netmask": netmask,
                "network": str(network),
                "mac": mac_address,
            }
        )

    return interfaces
