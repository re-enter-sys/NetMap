from netmap.topology import build_topology


def test_topology_contains_nodes_and_edges():
    interface = {
        "interface": "eth0",
        "ip": "10.10.10.10",
        "netmask": "255.255.255.0",
        "network": "10.10.10.0/24",
        "mac": "AA:BB:CC:DD:EE:10",
    }

    gateway = {
        "ip": "10.10.10.1",
        "interface": "eth0",
    }

    devices = [
        {
            "ip": "10.10.10.1",
            "hostname": "_gateway",
            "mac": "AA:BB:CC:DD:EE:01",
            "vendor": "VMware",
            "status": "up",
            "role": "Gateway",
        },
        {
            "ip": "10.10.10.154",
            "hostname": None,
            "mac": "AA:BB:CC:DD:EE:02",
            "vendor": "VMware",
            "status": "up",
            "role": "Device",
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

    topology = build_topology(
        interface,
        gateway,
        devices,
    )

    assert "nodes" in topology
    assert "edges" in topology

    assert len(topology["nodes"]) == 3
    assert len(topology["edges"]) == 2


def test_topology_roles():
    interface = {
        "interface": "eth0",
        "ip": "10.10.10.10",
        "netmask": "255.255.255.0",
        "network": "10.10.10.0/24",
        "mac": "AA:BB:CC:DD:EE:10",
    }

    gateway = {
        "ip": "10.10.10.1",
        "interface": "eth0",
    }

    devices = [
        {
            "ip": "10.10.10.1",
            "hostname": "_gateway",
            "mac": "AA:BB:CC:DD:EE:01",
            "vendor": "VMware",
            "status": "up",
            "role": "Gateway",
        },
    ]

    topology = build_topology(
        interface,
        gateway,
        devices,
    )

    roles = {
        node["ip"]: node["role"]
        for node in topology["nodes"]
    }

    assert roles["10.10.10.10"] == "Local Host"
    assert roles["10.10.10.1"] == "Gateway"


def test_topology_without_gateway():
    interface = {
        "interface": "eth0",
        "ip": "10.10.10.10",
        "netmask": "255.255.255.0",
        "network": "10.10.10.0/24",
        "mac": "AA:BB:CC:DD:EE:10",
    }

    devices = [
        {
            "ip": "10.10.10.154",
            "hostname": None,
            "mac": "AA:BB:CC:DD:EE:02",
            "vendor": "VMware",
            "status": "up",
            "role": "Device",
        },
    ]

    topology = build_topology(
        interface,
        None,
        devices,
    )

    assert len(topology["nodes"]) == 2
    assert len(topology["edges"]) == 0
