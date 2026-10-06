"""
NetMap - Port and service discovery.

Uses Nmap to identify TCP services on an authorized
network device.
"""

import re
import subprocess
from typing import Any


def scan_services(
    ip_address: str,
) -> list[dict[str, Any]]:
    """
    Discover open TCP ports and services.

    This intentionally uses a conservative Nmap scan.
    """

    command = [
        "nmap",
        "-sV",
        "--open",
        "-T3",
        ip_address,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return []

    services = []

    pattern = re.compile(
        r"^(\d+)/tcp\s+open\s+(\S+)(?:\s+(.*))?$"
    )

    for line in result.stdout.splitlines():

        line = line.strip()

        match = pattern.match(line)

        if not match:
            continue

        port = int(match.group(1))
        service = match.group(2)
        version = (
            match.group(3)
            or ""
        ).strip()

        services.append(
            {
                "port": port,
                "protocol": "tcp",
                "service": service,
                "version": version,
            }
        )

    return services
