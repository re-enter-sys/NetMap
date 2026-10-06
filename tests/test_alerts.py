from netmap.alerts import create_device_alert


def sample_device():
    return {
        "ip": "10.10.10.50",
        "hostname": "test-device",
        "mac": "AA:BB:CC:DD:EE:FF",
        "vendor": "Test Vendor",
        "role": "Device",
    }


def test_new_device_alert():
    alert = create_device_alert(
        sample_device(),
        "NEW_DEVICE",
    )

    assert alert["type"] == "NETWORK_DEVICE_CHANGE"
    assert alert["title"] == "New Network Device Detected"
    assert alert["severity"] == "MEDIUM"
    assert alert["device"]["ip"] == "10.10.10.50"


def test_removed_device_alert():
    alert = create_device_alert(
        sample_device(),
        "DEVICE_REMOVED",
    )

    assert alert["type"] == "NETWORK_DEVICE_REMOVED"
    assert alert["title"] == "Network Device Removed"
    assert alert["severity"] == "LOW"


def test_unknown_event_alert():
    alert = create_device_alert(
        sample_device(),
        "UNKNOWN_EVENT",
    )

    assert alert["type"] == "NETWORK_EVENT"
    assert alert["severity"] == "INFO"


def test_alert_contains_timestamp():
    alert = create_device_alert(
        sample_device(),
        "NEW_DEVICE",
    )

    assert "timestamp" in alert
    assert alert["timestamp"]


def test_alert_contains_device_details():
    alert = create_device_alert(
        sample_device(),
        "NEW_DEVICE",
    )

    device = alert["device"]

    assert device["hostname"] == "test-device"
    assert device["mac"] == "AA:BB:CC:DD:EE:FF"
    assert device["vendor"] == "Test Vendor"
    assert device["role"] == "Device"
