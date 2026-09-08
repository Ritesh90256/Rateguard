from fastapi.testclient import TestClient
import requests

from app.main import create_app
from app.redis_client import redis_client


def test_multiple_instances_share_rate_limit_state():
    key = "rateguard:window:Client-B"
    redis_client.delete(key)

    app_1 = create_app()
    app_2 = create_app()

    client_1 = TestClient(app_1)
    client_2 = TestClient(app_2)

    for _ in range(100):
        response = client_1.post(
            "/check",
            json={"client_id": "Client-B"}
        )

        assert response.status_code == 200
        assert response.json()["allowed"] is True

    response = client_2.post(
        "/check",
        json={"client_id": "Client-B"}
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is False

def test_multiple_instances_keep_client_state_separate():
    redis_client.delete("rateguard:window:Client-B")
    redis_client.delete("rateguard:window:Client-D")

    app_1 = create_app()
    app_2 = create_app()

    client_1 = TestClient(app_1)
    client_2 = TestClient(app_2)

    for _ in range(10):
        response = client_1.post(
            "/check",
            json={"client_id": "Client-B"}
        )

        assert response.json()["allowed"] is True

    response = client_2.post(
        "/check",
        json={"client_id": "Client-D"}
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is True

def test_nginx_preserves_shared_rate_limit():
    key = "rateguard:window:Client-B"
    redis_client.delete(key)

    responses = []

    for _ in range(100):
        response = requests.post(
            "http://127.0.0.1:8000/check",
            json={"client_id": "Client-B"}
        )

        assert response.status_code == 200
        responses.append(response.json())

    assert all(response["allowed"] is True for response in responses)

    response = requests.post(
        "http://127.0.0.1:8000/check",
        json={"client_id": "Client-B"}
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is False