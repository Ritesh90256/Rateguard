from app.tier_config import tier_config, client_tiers
from app.rate_limit_policy import RateLimitPolicy


def test_tier_config_contains_expected_tiers():
    assert "free" in tier_config
    assert "pro" in tier_config
    assert "enterprise" in tier_config


def test_tier_config_contains_policies():
    assert isinstance(tier_config["free"], RateLimitPolicy)
    assert isinstance(tier_config["pro"], RateLimitPolicy)
    assert isinstance(tier_config["enterprise"], RateLimitPolicy)


def test_client_tiers_map_clients_to_tiers():
    assert client_tiers["Client-A"] == "free"
    assert client_tiers["Client-B"] == "pro"
    assert client_tiers["Client-C"] == "enterprise"


def test_tier_policies_have_expected_values():
    assert tier_config["free"].algorithm == "token_bucket"
    assert tier_config["free"].capacity == 10
    assert tier_config["free"].refill_rate == 10

    assert tier_config["pro"].algorithm == "sliding_window_log"
    assert tier_config["pro"].limit == 100
    assert tier_config["pro"].window_size == 60

    assert tier_config["enterprise"].algorithm == "sliding_window_counter"
    assert tier_config["enterprise"].limit == 1000
    assert tier_config["enterprise"].window_size == 60