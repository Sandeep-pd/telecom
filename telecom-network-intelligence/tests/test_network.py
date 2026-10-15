from fastapi.testclient import TestClient

from app.main import app


def test_insert_and_get_measurement() -> None:
    with TestClient(app) as client:
        payload = {
            "cell_id": "CELL_102",
            "region": "Raipur",
            "network_type": "5G",
            "timestamp": "2025-01-01T10:00:00Z",
            "rsrp": -95,
            "rsrq": -10,
            "rssi": -70,
            "sinr": 18,
            "download_speed": 75.2,
            "upload_speed": 18.5,
            "latency": 25,
            "packet_loss": 0.5,
            "connected_users": 80,
            "call_drop_rate": 0.8,
            "handover_failure_rate": 1.2,
        }

        create_response = client.post("/network/data", json=payload)
        assert create_response.status_code == 201, create_response.text
        created_data = create_response.json()
        assert created_data["cell_id"] == "CELL_102"

        list_response = client.get("/network/data")
        assert list_response.status_code == 200
        assert len(list_response.json()) >= 1

        measurement_id = created_data["id"]
        detail_response = client.get(f"/network/data/{measurement_id}")
        assert detail_response.status_code == 200
        assert detail_response.json()["id"] == measurement_id

        cell_response = client.get("/network/cell/CELL_102")
        assert cell_response.status_code == 200
        assert any(item["cell_id"] == "CELL_102" for item in cell_response.json())


def test_invalid_measurement_input() -> None:
    with TestClient(app) as client:
        payload = {
            "cell_id": "CELL_102",
            "region": "Raipur",
            "network_type": "5G",
            "timestamp": "2025-01-01T10:00:00Z",
            "rsrp": -5,
            "rsrq": -10,
            "rssi": -70,
            "sinr": 18,
            "download_speed": 75.2,
            "upload_speed": 18.5,
            "latency": 25,
            "packet_loss": 0.5,
            "connected_users": 80,
            "call_drop_rate": 0.8,
            "handover_failure_rate": 1.2,
        }

        response = client.post("/network/data", json=payload)
        assert response.status_code == 422
