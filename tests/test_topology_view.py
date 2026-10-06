from netmap.topology_view import generate_topology_html


def test_generate_topology_html(tmp_path):
    topology = {
        "nodes": [
            {
                "id": "10.10.10.1",
                "label": "Gateway",
                "ip": "10.10.10.1",
                "role": "Gateway",
                "status": "up",
            },
            {
                "id": "10.10.10.10",
                "label": "Local Host",
                "ip": "10.10.10.10",
                "role": "Local Host",
                "status": "up",
            },
        ],
        "edges": [
            {
                "source": "10.10.10.1",
                "target": "10.10.10.10",
                "relationship": "gateway",
            }
        ],
    }

    output = tmp_path / "topology.html"

    result = generate_topology_html(
        topology,
        output,
    )

    assert result.exists()

    content = result.read_text(
        encoding="utf-8"
    )

    assert "<!DOCTYPE html>" in content
    assert "NetMap" in content
    assert "10.10.10.1" in content
    assert "10.10.10.10" in content
