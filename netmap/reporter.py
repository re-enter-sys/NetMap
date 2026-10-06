"""
NetMap - Scan report generation.

Exports discovered network information to JSON and CSV.
"""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_report(
    interface: dict[str, Any],
    gateway: dict[str, Any] | None,
    devices: list[dict[str, Any]],
    topology: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build a structured NetMap scan report.
    """

    report = {
        "project": "NetMap",
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "network": {
            "interface": interface["interface"],
            "ip": interface["ip"],
            "netmask": interface["netmask"],
            "network": interface["network"],
            "mac": interface["mac"],
            "gateway": gateway["ip"] if gateway else None,
        },
        "summary": {
            "active_devices": len(devices),
            "topology_nodes": len(topology["nodes"]) if topology else 0,
            "topology_edges": len(topology["edges"]) if topology else 0,
        },
        "devices": devices,
    }

    if topology:
        report["topology"] = topology

    return report


def export_json(
    report: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """
    Export a NetMap report to JSON.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    return path


def export_csv(
    devices: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    """
    Export discovered devices to CSV.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "ip",
        "hostname",
        "mac",
        "vendor",
        "status",
        "role",
    ]

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(devices)

    return path


def export_topology(
    topology: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """
    Export network topology to JSON.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(topology, file, indent=4)

    return path
