from app.limiter_factory import LimiterFactory
from app.token_bucket import TokenBucket
from app.sliding_window import SlidingWindowLog
import pytest
from app.sliding_window_counter import SlidingWindowCounter
from app.redis_client import redis_client
from app.redis_store import RedisStore

store = RedisStore(redis_client)

def test_factory_creates_token_bucket():
    factory = LimiterFactory(store)
    limiter = factory.create_limiter("token_bucket", "test-client")
    assert isinstance(limiter,TokenBucket)

def test_factory_creates_sliding_window_log() :
    factory = LimiterFactory(store)
    limiter = factory.create_limiter("sliding_window_log", "test-client")
    assert isinstance(limiter,SlidingWindowLog)

def test_factory_creates_sliding_window_counter():
     factory = LimiterFactory(store)
     limiter = factory.create_limiter("sliding_window_counter", "test-client")
     assert isinstance(limiter, SlidingWindowCounter)

def test_factory_rejects_invalid_algorithm():
        factory = LimiterFactory(store)
        with pytest.raises(ValueError):
            factory.create_limiter("banana", "test-client")