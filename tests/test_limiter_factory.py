from app.limiter_factory import LimiterFactory
from app.token_bucket import TokenBucket
from app.sliding_window import SlidingWindowLog
import pytest

def test_factory_creates_token_bucket():
    factory = LimiterFactory()
    limiter = factory.create_limiter("token_bucket")
    assert isinstance(limiter,TokenBucket)

def test_factory_creates_sliding_window_log() :
    factory = LimiterFactory()
    limiter = factory.create_limiter("sliding_window_log")
    assert isinstance(limiter,SlidingWindowLog)

def test_factory_rejects_invalid_algorithm():
        factory = LimiterFactory()
        with pytest.raises(ValueError):
            factory.create_limiter("banana")