"""
NetMap command-line interface.
"""
from netmap.live import run_monitor
from netmap.classifier import classify_device
from netmap.gateway import get_default_gateway
from netmap.network import get_interfaces
from netmap.reporter import (
    build_report,
    export_csv,
    export_json,
    export_topology,
)
from netmap.scanner import scan_network
from netmap.topology import build_topology
from netmap.topology_view import generate_topology_html


def main() -> None:
    """Discover local network and generate reports and topology."""

    print()
    print("=" * 60)
    print("                 NETMAP NETWORK DISCOVERY")
    print("=" * 60)
    print()

    # ---------------------------------------------------------
    # Network interface detection
    # ---------------------------------------------------------

    interfaces = get_interfaces()

    if not interfaces:
        print("[!] No usable IPv4 network interfaces detected.")
        return

    interface = interfaces[0]

    local_ip = interface["ip"]
    network = interface["network"]

    # ---------------------------------------------------------
    # Gateway detection
    # ---------------------------------------------------------

    gateway = get_default_gateway()

    gateway_ip = gateway["ip"] if gateway else None

    # ---------------------------------------------------------
    # Local network information
    # ---------------------------------------------------------

    print("LOCAL NETWORK")
    print("-" * 60)

    print(f"Interface : {interface['interface']}")
    print(f"IP        : {local_ip}")
    print(f"Netmask   : {interface['netmask']}")
    print(f"Network   : {network}")
    print(f"MAC       : {interface['mac']}")

    if gateway:
        print(f"Gateway   : {gateway_ip}")
    else:
        print("Gateway   : Not detected")

    print()

    # ---------------------------------------------------------
    # Network scan
    # ---------------------------------------------------------

    print(f"[+] Scanning network: {network}")
    print()

    try:
        devices = scan_network(network)
    except RuntimeError as error:
        print(f"[!] {error}")
        return

    # ---------------------------------------------------------
    # Device enrichment and classification
    # ---------------------------------------------------------

    for device in devices:

        if device["ip"] == local_ip:
            device["mac"] = interface["mac"]
            device["vendor"] = "Local"

        device["role"] = classify_device(
            device,
            local_ip,
            gateway_ip,
        )

    # ---------------------------------------------------------
    # Active devices
    # ---------------------------------------------------------

    print("=" * 60)
    print("                    ACTIVE DEVICES")
    print("=" * 60)
    print()

    for index, device in enumerate(devices, start=1):

        print(f"[{index}] {device['ip']}")
        print(f"    Hostname : {device['hostname'] or 'Unknown'}")
        print(f"    MAC      : {device['mac'] or 'Unknown'}")
        print(f"    Vendor   : {device['vendor'] or 'Unknown'}")
        print(f"    Status   : {device['status']}")
        print(f"    Role     : {device['role']}")
        print("-" * 60)

    print()
    print(f"[+] Active devices discovered: {len(devices)}")
    print()

    # ---------------------------------------------------------
    # Build topology
    # ---------------------------------------------------------

    topology = build_topology(
        interface,
        gateway,
        devices,
    )

    print(
        f"[+] Topology built: "
        f"{len(topology['nodes'])} nodes, "
        f"{len(topology['edges'])} edges"
    )

    print()

    # ---------------------------------------------------------
    # Build complete report
    # ---------------------------------------------------------

    report = build_report(
        interface,
        gateway,
        devices,
        topology,
    )

    # ---------------------------------------------------------
    # Export JSON
    # ---------------------------------------------------------

    json_path = export_json(
        report,
        "reports/netmap_report.json",
    )

    # ---------------------------------------------------------
    # Export CSV
    # ---------------------------------------------------------

    csv_path = export_csv(
        devices,
        "reports/netmap_devices.csv",
    )

    # ---------------------------------------------------------
    # Export topology JSON
    # ---------------------------------------------------------

    topology_path = export_topology(
        topology,
        "reports/netmap_topology.json",
    )

    # ---------------------------------------------------------
    # Generate topology HTML
    # ---------------------------------------------------------

    html_path = generate_topology_html(
        topology,
        "reports/netmap_topology.html",
    )

    # ---------------------------------------------------------
    # Report summary
    # ---------------------------------------------------------

    print("=" * 60)
    print("                    REPORTS")
    print("=" * 60)
    print()

    print(f"[+] JSON report    : {json_path}")
    print(f"[+] CSV report     : {csv_path}")
    print(f"[+] Topology JSON  : {topology_path}")
    print(f"[+] Topology HTML  : {html_path}")
    print()

    print("[+] NetMap scan completed successfully.")
    print()
    
def live() -> None:
    """Start live network monitoring."""

    interfaces = get_interfaces()

    if not interfaces:
        print("[!] No usable IPv4 network interface detected.")
        return

    network = interfaces[0]["network"]

    run_monitor(
        network,
        interval=10,
    )

if __name__ == "__main__":
    main()
