"""
NetMap - Live network monitoring.

Continuously scans the local network, detects device changes,
performs security enrichment, generates alerts, calculates risk,
stores historical data, and updates network topology.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from netmap.alerts import (
    create_device_alert,
    save_alert as save_database_alert,
)

from netmap.anomaly import detect_anomalies

from netmap.classifier import classify_device

from netmap.database import (
    init_database,
    save_event,
    save_services,
    save_topology,
    upsert_device,
)

from netmap.fingerprint import fingerprint_device

from netmap.gateway import get_default_gateway

from netmap.monitor import compare_devices

from netmap.network import get_interfaces

from netmap.os_detection import detect_os

from netmap.reporter import (
    build_report,
    export_json,
    export_topology,
)

from netmap.risk import calculate_device_risk

from netmap.scanner import scan_network

from netmap.services import scan_services

from netmap.topology import build_topology

from netmap.topology_view import generate_topology_html


# ============================================================================
# Runtime files
# ============================================================================

EVENT_LOG = Path(
    "reports/netmap_events.log"
)

HEARTBEAT_FILE = Path(
    "reports/netmap_heartbeat.json"
)

ALERT_FILE = Path(
    "reports/netmap_alerts.json"
)


# ============================================================================
# Logging
# ============================================================================

def log_event(message: str) -> None:
    """Write a timestamped event to console and log file."""

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

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

        file.write(
            event + "\n"
        )


# ============================================================================
# Heartbeat
# ============================================================================

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


# ============================================================================
# Legacy JSON alert persistence
# ============================================================================

def save_legacy_alert(
    alert: dict[str, Any],
) -> None:
    """
    Persist alerts to the legacy JSON file.

    SQLite is now the primary alert store, but the JSON file
    remains available for backwards compatibility.
    """

    ALERT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    alerts: list[dict[str, Any]] = []

    if ALERT_FILE.exists():

        try:

            with ALERT_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

                if isinstance(
                    data,
                    list,
                ):
                    alerts = data

        except (
            OSError,
            json.JSONDecodeError,
        ):

            alerts = []

    alerts.append(
        alert
    )

    with ALERT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            alerts[-100:],
            file,
            indent=4,
        )


# ============================================================================
# Database event helper
# ============================================================================

def persist_event(
    event_type: str,
    severity: str = "INFO",
    ip: str | None = None,
    message: str = "",
    data: dict[str, Any] | None = None,
) -> None:
    """
    Persist an event using the actual database.save_event() API.
    """

    timestamp = datetime.now().isoformat()

    try:

        save_event(
            timestamp,
            event_type,
            severity,
            ip,
            message,
            json.dumps(
                data or {},
                default=str,
            ),
        )

    except Exception as error:

        log_event(
            f"DATABASE_EVENT_ERROR "
            f"event={event_type} "
            f"ip={ip or 'N/A'} "
            f"error={error}"
        )


# ============================================================================
# Device enrichment
# ============================================================================

def enrich_devices(
    devices: list[dict[str, Any]],
    interface: dict[str, Any],
    gateway: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Add local information and classify device roles.
    """

    local_ip = interface["ip"]

    gateway_ip = (
        gateway["ip"]
        if gateway
        else None
    )

    for device in devices:

        ip_address = device["ip"]

        # ---------------------------------------------------------------
        # Local host
        # ---------------------------------------------------------------

        if ip_address == local_ip:

            device["mac"] = interface.get(
                "mac"
            )

            device["vendor"] = "Local"

        # ---------------------------------------------------------------
        # Role classification
        # ---------------------------------------------------------------

        device["role"] = classify_device(
            device,
            local_ip,
            gateway_ip,
        )

    return devices


# ============================================================================
# Security enrichment
# ============================================================================

def enrich_security_data(
    devices: list[dict[str, Any]],
    local_ip: str,
) -> list[dict[str, Any]]:
    """
    Perform advanced security enrichment.

    Adds:

    - service discovery
    - OS detection
    - device fingerprinting
    - risk scoring
    - SQLite persistence
    """

    print()
    print(
        "[*] Performing security enrichment..."
    )

    for device in devices:

        ip_address = device.get(
            "ip"
        )

        if not ip_address:
            continue

        is_local = (
            ip_address == local_ip
        )

        # ===============================================================
        # Service discovery
        # ===============================================================

        services: list[dict[str, Any]] = []

        if not is_local:

            try:

                print(
                    f"    [>] Service scan: "
                    f"{ip_address}"
                )

                services = scan_services(
                    ip_address
                )

                device["services"] = services

                if services:

                    print(
                        f"        [+] "
                        f"{len(services)} "
                        f"open service(s)"
                    )

                else:

                    print(
                        "        [-] "
                        "No open services detected"
                    )

            except Exception as error:

                device["services"] = []

                log_event(
                    f"SERVICE_SCAN_ERROR "
                    f"ip={ip_address} "
                    f"error={error}"
                )

        else:

            device["services"] = []

        # ===============================================================
        # OS detection
        # ===============================================================

        if not is_local:

            try:

                print(
                    f"    [>] OS detection: "
                    f"{ip_address}"
                )

                os_result = detect_os(
                    ip_address
                )

                # -------------------------------------------------------
                # Your detect_os() returns:
                #
                # {
                #     "os": "...",
                #     "confidence": ...
                # }
                #
                # SQLite cannot store the whole dictionary in os.
                # -------------------------------------------------------

                if isinstance(
                    os_result,
                    dict,
                ):

                    device["os"] = os_result.get(
                        "os"
                    )

                    device["os_confidence"] = (
                        os_result.get(
                            "confidence"
                        )
                    )

                else:

                    device["os"] = (
                        str(os_result)
                        if os_result
                        else None
                    )

                    device["os_confidence"] = None

                if device.get("os"):

                    print(
                        f"        [+] OS: "
                        f"{device['os']}"
                    )

                else:

                    print(
                        "        [-] OS not identified"
                    )

            except Exception as error:

                device["os"] = None
                device["os_confidence"] = None

                log_event(
                    f"OS_SCAN_ERROR "
                    f"ip={ip_address} "
                    f"error={error}"
                )

        else:

            device["os"] = None
            device["os_confidence"] = None

        # ===============================================================
        # Fingerprinting
        # ===============================================================

        try:

            fingerprint_device(
                device
            )

        except Exception as error:

            log_event(
                f"FINGERPRINT_ERROR "
                f"ip={ip_address} "
                f"error={error}"
            )

        # ===============================================================
        # Risk calculation
        # ===============================================================

        try:

            risk = calculate_device_risk(
                device
            )

            # -----------------------------------------------------------
            # Support both dictionary and numeric return values.
            # -----------------------------------------------------------

            if isinstance(
                risk,
                dict,
            ):

                device["risk_score"] = int(
                    risk.get(
                        "score",
                        0,
                    )
                    or 0
                )

                device["risk_level"] = (
                    risk.get(
                        "level",
                        "INFO",
                    )
                )

            elif isinstance(
                risk,
                (int, float),
            ):

                score = int(
                    risk
                )

                device["risk_score"] = score

                if score >= 90:
                    device["risk_level"] = "CRITICAL"

                elif score >= 70:
                    device["risk_level"] = "HIGH"

                elif score >= 40:
                    device["risk_level"] = "MEDIUM"

                elif score > 0:
                    device["risk_level"] = "LOW"

                else:
                    device["risk_level"] = "INFO"

            else:

                device["risk_score"] = 0
                device["risk_level"] = "INFO"

        except Exception as error:

            device["risk_score"] = 0
            device["risk_level"] = "INFO"

            log_event(
                f"RISK_CALCULATION_ERROR "
                f"ip={ip_address} "
                f"error={error}"
            )

        # ===============================================================
        # Device database persistence
        # ===============================================================

        device_id: int | None = None

        try:

            device_id = upsert_device(
                device
            )

        except Exception as error:

            log_event(
                f"DATABASE_DEVICE_ERROR "
                f"ip={ip_address} "
                f"error={error}"
            )

        # ===============================================================
        # Service database persistence
        # ===============================================================

        if (
            device_id is not None
            and services
        ):

            try:

                save_services(
                    device_id,
                    services,
                    datetime.now().isoformat(),
                )

            except Exception as error:

                log_event(
                    f"DATABASE_SERVICE_ERROR "
                    f"ip={ip_address} "
                    f"error={error}"
                )

        # ===============================================================
        # Security summary
        # ===============================================================

        print(
            f"    [*] {ip_address} "
            f"| type={device.get('device_type', 'Unknown')} "
            f"| risk={device.get('risk_score', 0)} "
            f"| level={device.get('risk_level', 'INFO')}"
        )

    print()

    return devices


# ============================================================================
# Topology
# ============================================================================

def update_topology(
    interface: dict[str, Any],
    gateway: dict[str, Any] | None,
    devices: list[dict[str, Any]],
) -> None:
    """
    Rebuild and export the current network topology.
    """

    topology = build_topology(
        interface,
        gateway,
        devices,
    )

    # -----------------------------------------------------------------------
    # JSON topology
    # -----------------------------------------------------------------------

    export_topology(
        topology,
        "reports/netmap_topology.json",
    )

    # -----------------------------------------------------------------------
    # Full report
    # -----------------------------------------------------------------------

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

    # -----------------------------------------------------------------------
    # Interactive topology
    # -----------------------------------------------------------------------

    generate_topology_html(
        topology,
        "reports/netmap_topology.html",
    )

    # -----------------------------------------------------------------------
    # Historical topology
    # -----------------------------------------------------------------------

    try:

        save_topology(
            topology
        )

    except Exception as error:

        log_event(
            f"DATABASE_TOPOLOGY_ERROR "
            f"error={error}"
        )

    print(
        f"[+] Topology updated: "
        f"{len(topology['nodes'])} nodes, "
        f"{len(topology['edges'])} edges"
    )


# ============================================================================
# Device change processing
# ============================================================================

def process_device_changes(
    added: list[dict[str, Any]],
    removed: list[dict[str, Any]],
) -> None:
    """
    Process newly discovered and removed devices.
    """

    # ========================================================================
    # New devices
    # ========================================================================

    for device in added:

        ip_address = device["ip"]

        hostname = (
            device.get("hostname")
            or "Unknown"
        )

        mac = (
            device.get("mac")
            or "Unknown"
        )

        log_event(
            f"NEW_DEVICE "
            f"ip={ip_address} "
            f"hostname={hostname} "
            f"mac={mac}"
        )

        persist_event(
            event_type="NEW_DEVICE",
            severity="MEDIUM",
            ip=ip_address,
            message=(
                f"New device discovered: "
                f"{hostname}"
            ),
            data=device,
        )

        try:

            alert = create_device_alert(
                device,
                "NEW_DEVICE",
            )

            # ---------------------------------------------------------------
            # SQLite
            # ---------------------------------------------------------------

            try:

                save_database_alert(
                    alert
                )

            except Exception as error:

                log_event(
                    f"DATABASE_ALERT_ERROR "
                    f"ip={ip_address} "
                    f"error={error}"
                )

            # ---------------------------------------------------------------
            # Legacy JSON
            # ---------------------------------------------------------------

            save_legacy_alert(
                alert
            )

            print(
                f"[!] SECURITY ALERT: "
                f"{alert['severity']} - "
                f"{alert['title']} - "
                f"{ip_address}"
            )

        except Exception as error:

            log_event(
                f"ALERT_CREATION_ERROR "
                f"event=NEW_DEVICE "
                f"ip={ip_address} "
                f"error={error}"
            )

    # ========================================================================
    # Removed devices
    # ========================================================================

    for device in removed:

        ip_address = device["ip"]

        hostname = (
            device.get("hostname")
            or "Unknown"
        )

        mac = (
            device.get("mac")
            or "Unknown"
        )

        log_event(
            f"DEVICE_REMOVED "
            f"ip={ip_address} "
            f"hostname={hostname} "
            f"mac={mac}"
        )

        persist_event(
            event_type="DEVICE_REMOVED",
            severity="LOW",
            ip=ip_address,
            message=(
                f"Device removed: "
                f"{hostname}"
            ),
            data=device,
        )

        try:

            alert = create_device_alert(
                device,
                "DEVICE_REMOVED",
            )

            try:

                save_database_alert(
                    alert
                )

            except Exception as error:

                log_event(
                    f"DATABASE_ALERT_ERROR "
                    f"ip={ip_address} "
                    f"error={error}"
                )

            save_legacy_alert(
                alert
            )

            print(
                f"[!] SECURITY ALERT: "
                f"{alert['severity']} - "
                f"{alert['title']} - "
                f"{ip_address}"
            )

        except Exception as error:

            log_event(
                f"ALERT_CREATION_ERROR "
                f"event=DEVICE_REMOVED "
                f"ip={ip_address} "
                f"error={error}"
            )


# ============================================================================
# Advanced anomaly detection
# ============================================================================

def process_anomalies(
    previous_devices: list[dict[str, Any]],
    current_devices: list[dict[str, Any]],
) -> None:
    """
    Detect advanced security anomalies.
    """

    try:

        anomalies = detect_anomalies(
            previous_devices,
            current_devices,
        )

    except Exception as error:

        log_event(
            f"ANOMALY_DETECTION_ERROR "
            f"error={error}"
        )

        return

    if not anomalies:
        return

    print()

    print(
        f"[!] SECURITY ANOMALIES DETECTED: "
        f"{len(anomalies)}"
    )

    for anomaly in anomalies:

        event_type = anomaly.get(
            "type",
            "UNKNOWN",
        )

        ip_address = anomaly.get(
            "ip",
            "Unknown",
        )

        description = anomaly.get(
            "description",
            "",
        )

        # ---------------------------------------------------------------
        # Determine severity
        # ---------------------------------------------------------------

        if event_type in {
            "MAC_CHANGE",
            "OS_CHANGE",
        }:

            severity = "HIGH"

        elif event_type in {
            "NEW_PORT",
            "PORT_CLOSED",
        }:

            severity = "MEDIUM"

        else:

            severity = "INFO"

        log_event(
            f"ANOMALY "
            f"type={event_type} "
            f"ip={ip_address} "
            f"description={description}"
        )

        persist_event(
            event_type=event_type,
            severity=severity,
            ip=ip_address,
            message=description,
            data=anomaly,
        )

        # ---------------------------------------------------------------
        # Build alert device
        # ---------------------------------------------------------------

        alert_device = {
            "ip": ip_address,
            "hostname": anomaly.get(
                "hostname"
            ),
            "mac": anomaly.get(
                "mac"
            ),
            "vendor": anomaly.get(
                "vendor"
            ),
            "device_type": anomaly.get(
                "device_type"
            ),
        }

        try:

            alert = create_device_alert(
                alert_device,
                event_type,
            )

            try:

                save_database_alert(
                    alert
                )

            except Exception as error:

                log_event(
                    f"DATABASE_ALERT_ERROR "
                    f"type={event_type} "
                    f"ip={ip_address} "
                    f"error={error}"
                )

            save_legacy_alert(
                alert
            )

            print(
                f"[!] ANOMALY ALERT: "
                f"{alert.get('severity', severity)} - "
                f"{event_type} - "
                f"{ip_address}"
            )

        except Exception as error:

            log_event(
                f"ANOMALY_ALERT_ERROR "
                f"type={event_type} "
                f"ip={ip_address} "
                f"error={error}"
            )


# ============================================================================
# Main monitoring loop
# ============================================================================

def run_monitor(
    network: str,
    interval: int = 10,
) -> None:
    """
    Continuously monitor a network.

    Args:
        network:
            IPv4 network in CIDR notation.

        interval:
            Seconds between scans.
    """

    # -----------------------------------------------------------------------
    # Banner
    # -----------------------------------------------------------------------

    print()

    print("=" * 70)
    print("                    NETMAP LIVE MONITOR")
    print("=" * 70)

    print()

    print(
        f"Network : {network}"
    )

    print(
        f"Interval: {interval} seconds"
    )

    print()

    # -----------------------------------------------------------------------
    # Database
    # -----------------------------------------------------------------------

    try:

        init_database()

        print(
            "[+] NetMap database initialized."
        )

    except Exception as error:

        print(
            f"[!] Database initialization failed: "
            f"{error}"
        )

        return

    # -----------------------------------------------------------------------
    # Interface
    # -----------------------------------------------------------------------

    interfaces = get_interfaces()

    if not interfaces:

        print(
            "[!] No usable IPv4 "
            "network interface detected."
        )

        return

    interface = interfaces[0]

    local_ip = interface["ip"]

    print(
        f"Interface: "
        f"{interface.get('interface', 'Unknown')}"
    )

    print(
        f"Local IP : {local_ip}"
    )

    print(
        f"Network  : "
        f"{interface.get('network', network)}"
    )

    # -----------------------------------------------------------------------
    # Gateway
    # -----------------------------------------------------------------------

    gateway = get_default_gateway()

    if gateway:

        print(
            f"Gateway  : "
            f"{gateway.get('ip', 'Unknown')}"
        )

    else:

        print(
            "Gateway  : Not detected"
        )

    print()

    # -----------------------------------------------------------------------
    # Initial scan
    # -----------------------------------------------------------------------

    print(
        "[*] Starting initial network scan..."
    )

    print()

    try:

        previous_devices = scan_network(
            network
        )

    except RuntimeError as error:

        print(
            f"[!] Initial scan failed: "
            f"{error}"
        )

        return

    # -----------------------------------------------------------------------
    # Basic enrichment
    # -----------------------------------------------------------------------

    previous_devices = enrich_devices(
        previous_devices,
        interface,
        gateway,
    )

    # -----------------------------------------------------------------------
    # Security enrichment
    # -----------------------------------------------------------------------

    previous_devices = enrich_security_data(
        previous_devices,
        local_ip,
    )

    # -----------------------------------------------------------------------
    # Heartbeat
    # -----------------------------------------------------------------------

    write_heartbeat(
        network,
        len(previous_devices),
    )

    # -----------------------------------------------------------------------
    # Monitor start event
    # -----------------------------------------------------------------------

    log_event(
        f"MONITOR_STARTED "
        f"network={network} "
        f"devices={len(previous_devices)}"
    )

    persist_event(
        event_type="MONITOR_STARTED",
        severity="INFO",
        message=(
            f"NetMap monitor started on "
            f"{network}"
        ),
        data={
            "network": network,
            "devices": len(previous_devices),
        },
    )

    # -----------------------------------------------------------------------
    # Initial topology
    # -----------------------------------------------------------------------

    update_topology(
        interface,
        gateway,
        previous_devices,
    )

    # -----------------------------------------------------------------------
    # Status
    # -----------------------------------------------------------------------

    print()

    print(
        f"[+] Initial devices discovered: "
        f"{len(previous_devices)}"
    )

    print()

    print(
        "[+] Security enrichment completed."
    )

    print()

    print(
        "[*] Monitoring for network changes..."
    )

    print(
        "[*] Press Ctrl+C to stop."
    )

    print()

    # ========================================================================
    # Continuous monitoring
    # ========================================================================

    try:

        while True:

            time.sleep(
                interval
            )

            print()
            print(
                "=" * 70
            )

            print(
                "[*] Running network scan..."
            )

            print(
                "=" * 70
            )

            # ---------------------------------------------------------------
            # Network scan
            # ---------------------------------------------------------------

            try:

                current_devices = scan_network(
                    network
                )

            except RuntimeError as error:

                log_event(
                    f"SCAN_ERROR "
                    f"error={error}"
                )

                continue

            # ---------------------------------------------------------------
            # Basic enrichment
            # ---------------------------------------------------------------

            current_devices = enrich_devices(
                current_devices,
                interface,
                gateway,
            )

            # ---------------------------------------------------------------
            # Security enrichment
            # ---------------------------------------------------------------

            current_devices = enrich_security_data(
                current_devices,
                local_ip,
            )

            # ---------------------------------------------------------------
            # Heartbeat
            # ---------------------------------------------------------------

            write_heartbeat(
                network,
                len(current_devices),
            )

            # ---------------------------------------------------------------
            # Compare devices
            # ---------------------------------------------------------------

            changes = compare_devices(
                previous_devices,
                current_devices,
            )

            added = changes.get(
                "added",
                [],
            )

            removed = changes.get(
                "removed",
                [],
            )

            # ---------------------------------------------------------------
            # Device changes
            # ---------------------------------------------------------------

            if added or removed:

                print()

                print(
                    "[!] Network changes detected:"
                )

                print(
                    f"    Added   : "
                    f"{len(added)}"
                )

                print(
                    f"    Removed : "
                    f"{len(removed)}"
                )

                process_device_changes(
                    added,
                    removed,
                )

            else:

                print()

                print(
                    f"[=] No device changes "
                    f"({len(current_devices)} active)"
                )

            # ---------------------------------------------------------------
            # Advanced anomalies
            # ---------------------------------------------------------------

            process_anomalies(
                previous_devices,
                current_devices,
            )

            # ---------------------------------------------------------------
            # Topology
            # ---------------------------------------------------------------

            update_topology(
                interface,
                gateway,
                current_devices,
            )

            # ---------------------------------------------------------------
            # Scan event
            # ---------------------------------------------------------------

            persist_event(
                event_type="SCAN_COMPLETED",
                severity="INFO",
                message=(
                    f"Network scan completed: "
                    f"{len(current_devices)} "
                    f"active devices"
                ),
                data={
                    "network": network,
                    "devices": len(
                        current_devices
                    ),
                    "added": len(
                        added
                    ),
                    "removed": len(
                        removed
                    ),
                },
            )

            # ---------------------------------------------------------------
            # New baseline
            # ---------------------------------------------------------------

            previous_devices = (
                current_devices
            )

    except KeyboardInterrupt:

        print()

        log_event(
            "MONITOR_STOPPED"
        )

        persist_event(
            event_type="MONITOR_STOPPED",
            severity="INFO",
            message=(
                "NetMap live monitor stopped."
            ),
            data={
                "network": network,
            },
        )

        print(
            "[+] NetMap monitor stopped."
        )

        print()


# ============================================================================
# Entry point
# ============================================================================

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
