
"""
NetMap - Live network monitoring.

Continuously scans the local network, detects device changes,
generates security alerts, and updates network topology.
"""

import json
import time
from datetime import datetime
from pathlib import Path

from netmap.alerts import create_device_alert
from netmap.classifier import classify_device
from netmap.gateway import get_default_gateway
from netmap.monitor import compare_devices
from netmap.network import get_interfaces
from netmap.reporter import build_report, export_json, export_topology
from netmap.scanner import scan_network
from netmap.topology import build_topology
from netmap.topology_view import generate_topology_html


EVENT_LOG = Path("reports/netmap_events.log")
HEARTBEAT_FILE = Path("reports/netmap_heartbeat.json")
ALERT_FILE = Path("reports/netmap_alerts.json")


def log_event(message: str) -> None:
    """Write a timestamped event to the console and log file."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    event = f"[{timestamp}] {message}"

    print(event)

    EVENT_LOG.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with EVENT_LOG.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(event + "\n")


def write_heartbeat(
    network: str,
    device_count: int,
) -> None:
    """Write the latest live-monitor heartbeat."""

    HEARTBEAT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    heartbeat = {
        "timestamp": datetime.now().isoformat(),
        "network": network,
        "devices": device_count,
        "status": "running",
    }

    with HEARTBEAT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            heartbeat,
            file,
            indent=4,
        )


def save_alert(alert: dict) -> None:
    """Persist security alerts to a JSON history file."""

    ALERT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    alerts = []

    if ALERT_FILE.exists():
        try:
            with ALERT_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:
                alerts = json.load(file)

                if not isinstance(alerts, list):
                    alerts = []

        except (
            OSError,
            json.JSONDecodeError,
        ):
            alerts = []

    alerts.append(alert)

    with ALERT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            alerts[-100:],
            file,
            indent=4,
        )


def enrich_devices(
    devices: list[dict],
    interface: dict,
    gateway: dict | None,
) -> list[dict]:
    """Add local information and device roles."""

    local_ip = interface["ip"]
    gateway_ip = gateway["ip"] if gateway else None

    for device in devices:

        if device["ip"] == local_ip:
            device["mac"] = interface["mac"]
            device["vendor"] = "Local"

        device["role"] = classify_device(
            device,
            local_ip,
            gateway_ip,
        )

    return devices


def update_topology(
    interface: dict,
    gateway: dict | None,
    devices: list[dict],
) -> None:
    """Rebuild and export the current network topology."""

    topology = build_topology(
        interface,
        gateway,
        devices,
    )

    export_topology(
        topology,
        "reports/netmap_topology.json",
    )

    report = build_report(
        interface,
        gateway,
        devices,
        topology,
    )

    export_json(
        report,
        "reports/netmap_report.json",
    )

    generate_topology_html(
        topology,
        "reports/netmap_topology.html",
    )

    print(
        f"[+] Topology updated: "
        f"{len(topology['nodes'])} nodes, "
        f"{len(topology['edges'])} edges"
    )


def process_device_changes(
    added: list[dict],
    removed: list[dict],
) -> None:
    """Log device changes and generate security alerts."""

    for device in added:

        log_event(
            f"NEW_DEVICE "
            f"ip={device['ip']} "
            f"hostname={device.get('hostname') or 'Unknown'} "
            f"mac={device.get('mac') or 'Unknown'}"
        )

        alert = create_device_alert(
            device,
            "NEW_DEVICE",
        )

        save_alert(alert)

        print(
            f"[!] SECURITY ALERT: "
            f"{alert['severity']} - "
            f"{alert['title']} - "
            f"{device['ip']}"
        )

    for device in removed:

        log_event(
            f"DEVICE_REMOVED "
            f"ip={device['ip']} "
            f"hostname={device.get('hostname') or 'Unknown'} "
            f"mac={device.get('mac') or 'Unknown'}"
        )

        alert = create_device_alert(
            device,
            "DEVICE_REMOVED",
        )

        save_alert(alert)

        print(
            f"[!] SECURITY ALERT: "
            f"{alert['severity']} - "
            f"{alert['title']} - "
            f"{device['ip']}"
        )


def run_monitor(
    network: str,
    interval: int = 10,
) -> None:
    """
    Continuously monitor a network.

    Args:
        network: IPv4 network in CIDR notation.
        interval: Seconds between scans.
    """

    print()
    print("=" * 60)
    print("                 NETMAP LIVE MONITOR")
    print("=" * 60)
    print()
    print(f"Network : {network}")
    print(f"Interval: {interval} seconds")
    print()

    interfaces = get_interfaces()

    if not interfaces:
        print("[!] No usable IPv4 network interface detected.")
        return

    interface = interfaces[0]
    gateway = get_default_gateway()

    print("[*] Starting initial scan...")
    print()

    try:
        previous_devices = scan_network(network)

    except RuntimeError as error:
        print(f"[!] Initial scan failed: {error}")
        return

    previous_devices = enrich_devices(
        previous_devices,
        interface,
        gateway,
    )

    write_heartbeat(
        network,
        len(previous_devices),
    )

    log_event(
        f"MONITOR_STARTED "
        f"network={network} "
        f"devices={len(previous_devices)}"
    )

    update_topology(
        interface,
        gateway,
        previous_devices,
    )

    print()
    print(
        f"[+] Initial devices discovered: "
        f"{len(previous_devices)}"
    )
    print()
    print("[*] Monitoring for changes...")
    print("[*] Press Ctrl+C to stop.")
    print()

    try:

        while True:

            time.sleep(interval)

            print("[*] Running scan...")

            try:
                current_devices = scan_network(network)

            except RuntimeError as error:
                log_event(
                    f"SCAN_ERROR error={error}"
                )
                continue

            current_devices = enrich_devices(
                current_devices,
                interface,
                gateway,
            )

            write_heartbeat(
                network,
                len(current_devices),
            )

            changes = compare_devices(
                previous_devices,
                current_devices,
            )

            added = changes["added"]
            removed = changes["removed"]

            if added or removed:

                process_device_changes(
                    added,
                    removed,
                )

                update_topology(
                    interface,
                    gateway,
                    current_devices,
                )

            else:

                print(
                    f"[=] No device changes "
                    f"({len(current_devices)} active)"
                )

            previous_devices = current_devices

    except KeyboardInterrupt:

        log_event(
            "MONITOR_STOPPED"
        )

        print()


if __name__ == "__main__":

    interfaces = get_interfaces()

    if not interfaces:

        print(
            "[!] No usable IPv4 network "
            "interface detected."
        )

    else:

        network = interfaces[0]["network"]

        run_monitor(
            network,
            interval=10,
        )
