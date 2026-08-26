from fastapi.testclient import TestClient
from app.main import app, limiters
from app.redis_client import redis_client
from app.redis_store import RedisStore

client = TestClient(app)
store = RedisStore(redis_client)

def test_check_endpoint_uses_redis_token_bucket():
    store.delete("rateguard:bucket:redis-integration-test-client")

    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.status_code == 200
    assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.json() == {"allowed": True}
    
    response = client.post(
        "/check",
        json={"client_id": "redis-integration-test-client"}
    )
    assert response.json() == {"allowed": False}

def test_check_endpoint_uses_redis_sliding_window():
    client_id = "Client-B"
    key = f"rateguard:window:{client_id}"

    store.delete(key)
    limiters.pop(client_id, None)

    for _ in range(10):
        response = client.post(
            "/check",
            json={"client_id": client_id}
        )

        assert response.status_code == 200
        assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert response.status_code == 200
    assert response.json() == {"allowed": False}

def test_check_endpoint_uses_redis_sliding_window_counter():
    client_id = "Client-C"
    key = f"rateguard:counter:{client_id}"

    store.delete(key)
    limiters.pop(client_id, None)

    for _ in range(10):
        response = client.post(
            "/check",
            json={"client_id": client_id}
        )

        assert response.status_code == 200
        assert response.json() == {"allowed": True}

    response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert response.status_code == 200
    assert response.json() == {"allowed": False}

