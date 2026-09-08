from fastapi.testclient import TestClient

from app.main import app, limiters
from app.redis_client import redis_client
from app.redis_store import RedisStore
from app.config_store import ConfigStore
from app.tier_config import tier_config


client = TestClient(app)
store = RedisStore(redis_client)
config_store = ConfigStore(redis_client)


def test_check_endpoint_uses_redis_token_bucket():
    client_id = "redis-integration-test-client"

    limiter_key = f"rateguard:bucket:{client_id}"
    client_key = f"rateguard:config:client:{client_id}"

    redis_client.delete(limiter_key)
    redis_client.delete(client_key)
    limiters.pop(client_id, None)

    config_store.set_client_tier(client_id, "free")
    config_store.set_tier_policy("free", tier_config["free"])

    for _ in range(10):
        response = client.post(
            "/check",
            json={"client_id": client_id}
        )

        assert response.status_code == 200
        assert response.json()["allowed"] is True

    response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is False


def test_check_endpoint_uses_redis_sliding_window():
    client_id = "Client-B"

    limiter_key = f"rateguard:window:{client_id}"
    client_key = f"rateguard:config:client:{client_id}"

    redis_client.delete(limiter_key)
    redis_client.delete(client_key)
    limiters.pop(client_id, None)

    config_store.set_client_tier(client_id, "pro")
    config_store.set_tier_policy("pro", tier_config["pro"])

    for _ in range(100):
        response = client.post(
            "/check",
            json={"client_id": client_id}
        )

        assert response.status_code == 200
        assert response.json()["allowed"] is True

    response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is False


def test_check_endpoint_uses_redis_sliding_window_counter():
    client_id = "Client-C"

    limiter_key = f"rateguard:counter:{client_id}"
    client_key = f"rateguard:config:client:{client_id}"

    redis_client.delete(limiter_key)
    redis_client.delete(client_key)
    limiters.pop(client_id, None)

    config_store.set_client_tier(client_id, "enterprise")
    config_store.set_tier_policy("enterprise", tier_config["enterprise"])

    for _ in range(1000):
        response = client.post(
            "/check",
            json={"client_id": client_id}
        )

        assert response.status_code == 200
        assert response.json()["allowed"] is True

    response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert response.status_code == 200
    assert response.json()["allowed"] is False