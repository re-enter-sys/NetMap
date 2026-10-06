import json

from netmap.reporter import (
    build_report,
    export_csv,
    export_json,
)


def sample_interface():
    return {
        "interface": "eth0",
        "ip": "10.10.10.10",
        "netmask": "255.255.255.0",
        "network": "10.10.10.0/24",
        "mac": "AA:BB:CC:DD:EE:10",
    }


def sample_gateway():
    return {
        "ip": "10.10.10.1",
        "interface": "eth0",
    }


def sample_devices():
    return [
        {
            "ip": "10.10.10.1",
            "hostname": "_gateway",
            "mac": "AA:BB:CC:DD:EE:01",
            "vendor": "VMware",
            "status": "up",
            "role": "Gateway",
        },
        {
            "ip": "10.10.10.10",
            "hostname": "security-monitor.local",
            "mac": "AA:BB:CC:DD:EE:10",
            "vendor": "Local",
            "status": "up",
            "role": "Local Host",
        },
    ]


def test_build_report():
    report = build_report(
        sample_interface(),
        sample_gateway(),
        sample_devices(),
    )

    assert report["project"] == "NetMap"
    assert "scan_timestamp" in report
    assert report["network"]["interface"] == "eth0"
    assert report["network"]["gateway"] == "10.10.10.1"
    assert report["summary"]["active_devices"] == 2
    assert len(report["devices"]) == 2


def test_export_json(tmp_path):
    report = build_report(
        sample_interface(),
        sample_gateway(),
        sample_devices(),
    )

    output = tmp_path / "report.json"

    result = export_json(report, output)

    assert result.exists()

    with result.open(encoding="utf-8") as file:
        data = json.load(file)

    assert data["project"] == "NetMap"
    assert len(data["devices"]) == 2


def test_export_csv(tmp_path):
    devices = sample_devices()

    output = tmp_path / "devices.csv"

    result = export_csv(devices, output)

    assert result.exists()

    content = output.read_text(encoding="utf-8")

    assert "ip,hostname,mac,vendor,status,role" in content
    assert "10.10.10.1" in content
    assert "Gateway" in content
