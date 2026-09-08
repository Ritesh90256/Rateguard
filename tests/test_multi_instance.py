from fastapi.testclient import TestClient
import requests

from app.main import create_app
from app.redis_client import redis_client
from app.config_store import ConfigStore
from app.tier_config import tier_config


config_store = ConfigStore(redis_client)


def test_multiple_instances_share_rate_limit_state():
    client_id = "Client-B"

    limiter_key = f"rateguard:window:{client_id}"
    client_key = f"rateguard:config:client:{client_id}"

    redis_client.delete(limiter_key)
    redis_client.delete(client_key)

    config_store.set_client_tier(client_id, "pro")
    config_store.set_tier_policy("pro", tier_config["pro"])

    app_1 = create_app()
    app_2 = create_app()

    client_1 = TestClient(app_1)
    client_2 = TestClient(app_2)

    for _ in range(100):
        response = client_1.post(
            "/check",
            json={"client_id": client_id}
        )

        assert response.status_code == 200
        assert response.json()["allowed"] is True

    response = client_2.post(
        "/check",
        json={"client_id": client_id}
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is False


def test_multiple_instances_keep_client_state_separate():
    client_b = "Client-B"
    client_d = "Client-D"

    redis_client.delete(f"rateguard:window:{client_b}")
    redis_client.delete(f"rateguard:config:client:{client_b}")

    redis_client.delete(f"rateguard:window:{client_d}")
    redis_client.delete(f"rateguard:config:client:{client_d}")

    config_store.set_client_tier(client_b, "pro")
    config_store.set_tier_policy("pro", tier_config["pro"])

    config_store.set_client_tier(client_d, "free")
    config_store.set_tier_policy("free", tier_config["free"])

    app_1 = create_app()
    app_2 = create_app()

    client_1 = TestClient(app_1)
    client_2 = TestClient(app_2)

    for _ in range(10):
        response = client_1.post(
            "/check",
            json={"client_id": client_b}
        )

        assert response.status_code == 200
        assert response.json()["allowed"] is True

    response = client_2.post(
        "/check",
        json={"client_id": client_d}
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is True


def test_nginx_preserves_shared_rate_limit():
    client_id = "Client-B"

    limiter_key = f"rateguard:window:{client_id}"
    client_key = f"rateguard:config:client:{client_id}"

    redis_client.delete(limiter_key)
    redis_client.delete(client_key)

    config_store.set_client_tier(client_id, "pro")
    config_store.set_tier_policy("pro", tier_config["pro"])

    responses = []

    for _ in range(100):
        response = requests.post(
            "http://127.0.0.1:8000/check",
            json={"client_id": client_id}
        )

        assert response.status_code == 200
        responses.append(response.json())

    assert all(response["allowed"] is True for response in responses)

    response = requests.post(
        "http://127.0.0.1:8000/check",
        json={"client_id": client_id}
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is False