from netmap.gateway import get_default_gateway


def test_gateway_structure():
    gateway = get_default_gateway()

    assert gateway is None or isinstance(gateway, dict)

    if gateway:
        assert "ip" in gateway
        assert "interface" in gateway
