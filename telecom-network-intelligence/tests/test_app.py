from fastapi.testclient import TestClient

from app.main import app


def test_root_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Telecom Network Intelligence Platform is running"


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "telecom-network-intelligence"}


def test_analytics_summary_endpoint() -> None:
    with TestClient(app) as client:
        payload = {
            "cell_id": "CELL_200",
            "region": "Bhopal",
            "network_type": "5G",
            "timestamp": "2025-02-01T12:00:00Z",
            "rsrp": -94,
            "rsrq": -12,
            "rssi": -71,
            "sinr": 16,
            "download_speed": 80,
            "upload_speed": 22,
            "latency": 30,
            "packet_loss": 0.8,
            "connected_users": 90,
            "call_drop_rate": 1.0,
            "handover_failure_rate": 1.4,
        }

        create_response = client.post("/network/data", json=payload)
        assert create_response.status_code == 201

        response = client.get("/analytics/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["snapshot"]["total_measurements"] >= 1
        assert data["snapshot"]["active_cells"] >= 1

        trend_response = client.get("/analytics/trends")
        assert trend_response.status_code == 200
        trend_data = trend_response.json()
        assert trend_data["status"] == "ready"
        assert len(trend_data["points"]) >= 1
        assert "latency" in trend_data["series"]


def test_local_network_status_endpoint(monkeypatch) -> None:
    from app.services import local_network_service

    monkeypatch.setattr(
        local_network_service,
        "_internet_probe",
        lambda: {"reachable": True, "latency_ms": 12.3},
    )
    monkeypatch.setattr(local_network_service, "_wifi_details", lambda: None)

    with TestClient(app) as client:
        response = client.get("/network/local-status")

    assert response.status_code == 200
    data = response.json()
    assert data["computer_name"]
    assert data["operating_system"]
    assert data["internet"] == {"reachable": True, "latency_ms": 12.3}
    assert isinstance(data["interfaces"], list)
    if data["interfaces"]:
        interface = data["interfaces"][0]
        assert "name" in interface
        assert "is_up" in interface
        assert "addresses" in interface
        assert "receive_bytes_per_second" in interface
        assert "transmit_bytes_per_second" in interface


def test_auth_token_endpoint(monkeypatch) -> None:
    from app.core import security

    monkeypatch.setattr(security.settings, "require_auth", True)
    with TestClient(app) as client:
        bad_login = client.post(
            "/auth/token",
            json={"username": "admin", "password": "incorrect"},
        )
        assert bad_login.status_code == 401

        response = client.post(
            "/auth/token",
            json={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 200
        auth_data = response.json()
        token = auth_data["access_token"]
        assert auth_data["token_type"] == "bearer"
        assert auth_data["expires_in"] > 0

        unauthenticated_response = client.get("/auth/validate")
        assert unauthenticated_response.status_code == 401
        protected_response = client.get("/network/data")
        assert protected_response.status_code == 401

        validate_response = client.get(
            "/auth/validate",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert validate_response.status_code == 200
        assert validate_response.json()["status"] == "valid"
        assert validate_response.json()["username"] == "admin"
        protected_response = client.get(
            "/network/data",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert protected_response.status_code == 200

        invalid_token_response = client.get(
            "/auth/validate",
            headers={"Authorization": "Bearer invalid.token.value"},
        )
        assert invalid_token_response.status_code == 401
