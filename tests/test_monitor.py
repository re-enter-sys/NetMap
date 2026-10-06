from netmap.monitor import compare_devices


def device(ip, role="Device"):
    return {
        "ip": ip,
        "hostname": None,
        "mac": None,
        "vendor": None,
        "status": "up",
        "role": role,
    }


def test_detect_added_device():
    previous = [
        device("10.10.10.1", "Gateway"),
        device("10.10.10.10", "Local Host"),
    ]

    current = [
        device("10.10.10.1", "Gateway"),
        device("10.10.10.10", "Local Host"),
        device("10.10.10.50"),
    ]

    result = compare_devices(previous, current)

    assert len(result["added"]) == 1
    assert result["added"][0]["ip"] == "10.10.10.50"

    assert len(result["removed"]) == 0
    assert len(result["unchanged"]) == 2


def test_detect_removed_device():
    previous = [
        device("10.10.10.1", "Gateway"),
        device("10.10.10.10", "Local Host"),
        device("10.10.10.50"),
    ]

    current = [
        device("10.10.10.1", "Gateway"),
        device("10.10.10.10", "Local Host"),
    ]

    result = compare_devices(previous, current)

    assert len(result["added"]) == 0
    assert len(result["removed"]) == 1
    assert result["removed"][0]["ip"] == "10.10.10.50"
    assert len(result["unchanged"]) == 2


def test_detect_added_and_removed_devices():
    previous = [
        device("10.10.10.1", "Gateway"),
        device("10.10.10.10", "Local Host"),
        device("10.10.10.50"),
    ]

    current = [
        device("10.10.10.1", "Gateway"),
        device("10.10.10.10", "Local Host"),
        device("10.10.10.75"),
    ]

    result = compare_devices(previous, current)

    assert len(result["added"]) == 1
    assert result["added"][0]["ip"] == "10.10.10.75"

    assert len(result["removed"]) == 1
    assert result["removed"][0]["ip"] == "10.10.10.50"

    assert len(result["unchanged"]) == 2


def test_identical_scans():
    devices = [
        device("10.10.10.1", "Gateway"),
        device("10.10.10.10", "Local Host"),
    ]

    result = compare_devices(devices, devices)

    assert result["added"] == []
    assert result["removed"] == []
    assert len(result["unchanged"]) == 2
