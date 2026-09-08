from app.limiter_factory import LimiterFactory
from app.token_bucket import TokenBucket
from app.sliding_window import SlidingWindowLog
from app.sliding_window_counter import SlidingWindowCounter
from app.redis_client import redis_client
from app.redis_store import RedisStore
from app.rate_limit_policy import RateLimitPolicy
import pytest


store = RedisStore(redis_client)


def test_factory_creates_token_bucket():
    factory = LimiterFactory(store)

    policy = RateLimitPolicy(
        algorithm="token_bucket",
        limit=10,
        window_size=60,
        capacity=10,
        refill_rate=10
    )

    limiter = factory.create_limiter(policy, "test-token-client")

    assert isinstance(limiter, TokenBucket)


def test_factory_creates_sliding_window_log():
    factory = LimiterFactory(store)

    policy = RateLimitPolicy(
        algorithm="sliding_window_log",
        limit=10,
        window_size=60,
        capacity=10,
        refill_rate=10
    )

    limiter = factory.create_limiter(policy, "test-log-client")

    assert isinstance(limiter, SlidingWindowLog)


def test_factory_creates_sliding_window_counter():
    factory = LimiterFactory(store)

    policy = RateLimitPolicy(
        algorithm="sliding_window_counter",
        limit=10,
        window_size=60,
        capacity=10,
        refill_rate=10
    )

    limiter = factory.create_limiter(policy, "test-counter-client")

    assert isinstance(limiter, SlidingWindowCounter)


def test_factory_rejects_invalid_algorithm():
    factory = LimiterFactory(store)

    policy = RateLimitPolicy(
        algorithm="banana",
        limit=10,
        window_size=60,
        capacity=10,
        refill_rate=10
    )

    with pytest.raises(ValueError):
        factory.create_limiter(policy, "test-invalid-client")


def test_factory_uses_token_bucket_policy():
    factory = LimiterFactory(store)

    policy = RateLimitPolicy(
        algorithm="token_bucket",
        limit=20,
        window_size=120,
        capacity=20,
        refill_rate=5
    )

    limiter = factory.create_limiter(policy, "test-policy-token")

    assert limiter.capacity == 20
    assert limiter.refill_rate == 5


def test_factory_uses_window_policy():
    factory = LimiterFactory(store)

    policy = RateLimitPolicy(
        algorithm="sliding_window_log",
        limit=25,
        window_size=120,
        capacity=25,
        refill_rate=5
    )

    limiter = factory.create_limiter(policy, "test-policy-window")

    assert limiter.limit == 25
    assert limiter.window_size == 120

