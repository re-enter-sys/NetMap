from netmap.classifier import classify_device


def test_classify_local_host():
    device = {"ip": "10.10.10.10"}

    assert (
        classify_device(
            device,
            "10.10.10.10",
            "10.10.10.1",
        )
        == "Local Host"
    )


def test_classify_gateway():
    device = {"ip": "10.10.10.1"}

    assert (
        classify_device(
            device,
            "10.10.10.10",
            "10.10.10.1",
        )
        == "Gateway"
    )


def test_classify_device():
    device = {"ip": "10.10.10.154"}

    assert (
        classify_device(
            device,
            "10.10.10.10",
            "10.10.10.1",
        )
        == "Device"
    )
