from fastapi.testclient import TestClient
from app.main import create_app
from app.redis_client import redis_client
from app.config_store import ConfigStore
from app.rate_limit_policy import RateLimitPolicy

config_store = ConfigStore(redis_client)

def test_configuration_change_takes_effect_without_restart():
    client_id = "Client-H"

    client_key = f"rateguard:config:client:{client_id}"
    tier_key = "rateguard:config:tier:test-free"
    limiter_key = f"rateguard:bucket:{client_id}"

    redis_client.delete(limiter_key)
    redis_client.delete(client_key)
    redis_client.delete(tier_key)

    config_store.set_client_tier(client_id, "test-free")

    initial_policy = RateLimitPolicy(
        algorithm="token_bucket",
        limit=1,
        window_size=60,
        capacity=1,
        refill_rate=1
    )

    config_store.set_tier_policy("test-free", initial_policy)

    app = create_app()
    client = TestClient(app)

    first_response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert first_response.json()["allowed"] is True

    updated_policy = RateLimitPolicy(
        algorithm="token_bucket",
        limit=2,
        window_size=60,
        capacity=2,
        refill_rate=2
    )

    config_store.set_tier_policy("test-free", updated_policy)

    second_response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert second_response.status_code == 200
    assert app.limiter_policies[client_id] == updated_policy

def test_configuration_change_is_visible_to_multiple_instances():
    client_id = "Client-I"
    client_key = f"rateguard:config:client:{client_id}"
    tier_key = "rateguard:config:tier:test-multi"
    limiter_key = f"rateguard:bucket:{client_id}"

    redis_client.delete(client_key)
    redis_client.delete(tier_key)
    redis_client.delete(limiter_key)

    config_store.set_client_tier(client_id, "test-multi")

    initial_policy = RateLimitPolicy(
        algorithm="token_bucket",
        limit=1,
        window_size=60,
        capacity=1,
        refill_rate=1
    )

    config_store.set_tier_policy("test-multi", initial_policy)

    app_1 = create_app()
    app_2 = create_app()

    client_1 = TestClient(app_1)
    client_2 = TestClient(app_2)

    response_1 = client_1.post(
        "/check",
        json={"client_id": client_id}
    )

    assert response_1.json()["allowed"] is True

    updated_policy = RateLimitPolicy(
        algorithm="token_bucket",
        limit=2,
        window_size=60,
        capacity=2,
        refill_rate=2
    )

    config_store.set_tier_policy("test-multi", updated_policy)

    response_2 = client_2.post(
        "/check",
        json={"client_id": client_id}
    )

    assert response_2.status_code == 200
    assert app_2.limiter_policies[client_id] == updated_policy

def test_client_tier_change_takes_effect_without_restart():
    client_id = "Client-J"

    client_key = f"rateguard:config:client:{client_id}"

    redis_client.delete(client_key)

    config_store.set_client_tier(client_id, "free")

    app = create_app()
    client = TestClient(app)

    first_response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert first_response.status_code == 200
    assert app.limiter_policies[client_id].algorithm == "token_bucket"

    config_store.set_client_tier(client_id, "pro")

    second_response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert second_response.status_code == 200
    assert app.limiter_policies[client_id].algorithm == "sliding_window_log"

def test_unchanged_configuration_reuses_existing_limiter():
    client_id = "Client-K"
    client_key = f"rateguard:config:client:{client_id}"
    tier_key = "rateguard:config:tier:test-reuse"

    redis_client.delete(client_key)
    redis_client.delete(tier_key)

    config_store.set_client_tier(client_id, "test-reuse")

    policy = RateLimitPolicy(
        algorithm="token_bucket",
        limit=10,
        window_size=60,
        capacity=10,
        refill_rate=10
    )

    config_store.set_tier_policy("test-reuse", policy)

    app = create_app()
    client = TestClient(app)

    first_response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert first_response.status_code == 200

    first_limiter = app.limiters[client_id]

    second_response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert second_response.status_code == 200

    second_limiter = app.limiters[client_id]

    assert first_limiter is second_limiter

def test_cached_instance_reloads_after_configuration_change():
    client_id = "Client-L"

    client_key = f"rateguard:config:client:{client_id}"
    tier_key = "rateguard:config:tier:test-cached"
    limiter_key = f"rateguard:bucket:{client_id}"

    redis_client.delete(client_key)
    redis_client.delete(tier_key)
    redis_client.delete(limiter_key)

    config_store.set_client_tier(client_id, "test-cached")

    initial_policy = RateLimitPolicy(
        algorithm="token_bucket",
        limit=1,
        window_size=60,
        capacity=1,
        refill_rate=1
    )

    config_store.set_tier_policy("test-cached", initial_policy)

    app = create_app()
    client = TestClient(app)

    first_response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert first_response.json()["allowed"] is True
    assert app.limiter_policies[client_id] == initial_policy

    updated_policy = RateLimitPolicy(
        algorithm="token_bucket",
        limit=10,
        window_size=60,
        capacity=10,
        refill_rate=10
    )

    config_store.set_tier_policy("test-cached", updated_policy)

    second_response = client.post(
        "/check",
        json={"client_id": client_id}
    )

    assert second_response.status_code == 200
    assert app.limiter_policies[client_id] == updated_policy
