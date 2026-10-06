from netmap.scanner import scan_network


def test_scan_network_returns_list():
    devices = scan_network("127.0.0.1/32")

    assert isinstance(devices, list)


def test_device_structure():
    devices = scan_network("127.0.0.1/32")

    for device in devices:
        assert "ip" in device
        assert "hostname" in device
        assert "mac" in device
        assert "vendor" in device
        assert "status" in device
