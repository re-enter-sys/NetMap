from netmap.network import get_interfaces


def test_get_interfaces_returns_list():
    interfaces = get_interfaces()

    assert isinstance(interfaces, list)


def test_interface_structure():
    interfaces = get_interfaces()

    for interface in interfaces:
        assert "interface" in interface
        assert "ip" in interface
        assert "netmask" in interface
        assert "network" in interface
        assert "mac" in interface
