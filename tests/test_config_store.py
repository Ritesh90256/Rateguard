from app.config_store import ConfigStore
from app.redis_client import redis_client
from app.rate_limit_policy import RateLimitPolicy

config_store = ConfigStore(redis_client)

def test_config_store_sets_and_gets_client_tier():
    client_id = "test-config-client"
    key = f"rateguard:config:client:{client_id}"

    redis_client.delete(key)

    config_store.set_client_tier(client_id, "pro")

    assert config_store.get_client_tier(client_id) == "pro"

def test_config_store_sets_and_gets_tier_policy():
    tier = "test-pro"
    key = f"rateguard:config:tier:{tier}"

    redis_client.delete(key)

    policy = RateLimitPolicy(
        algorithm="sliding_window_log",
        limit=100,
        window_size=60,
        capacity=100,
        refill_rate=100
    )

    config_store.set_tier_policy(tier, policy)

    result = config_store.get_tier_policy(tier)

    assert isinstance(result, RateLimitPolicy)
    assert result.algorithm == "sliding_window_log"
    assert result.limit == 100
    assert result.window_size == 60
    assert result.capacity == 100
    assert result.refill_rate == 100

def test_config_version_starts_at_zero():
    redis_client.delete("rateguard:config:version")

    assert config_store.get_config_version() == 0


def test_config_version_increments():
    redis_client.delete("rateguard:config:version")

    assert config_store.increment_config_version() == 1
    assert config_store.increment_config_version() == 2
