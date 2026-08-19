from app.token_bucket import TokenBucket
from app.sliding_window import SlidingWindowLog

current_time = [0]
def fake_clock():
    return current_time[0]

def test_token_bucket_allows_limit():
    current_time[0] = 0
    bucket = TokenBucket(3,10,fake_clock)
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True

def test_token_bucket_denies_after_limit():
    current_time[0] = 0
    bucket = TokenBucket(3,10,fake_clock)
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is False

def test_token_bucket_refills():
    current_time[0] = 0
    bucket = TokenBucket(3,10,fake_clock)
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    current_time[0] = 6
    assert bucket.allow_request() is True

def test_token_bucket_never_exceeds_capacity():
    current_time[0] = 0
    bucket = TokenBucket(3,10,fake_clock)
    assert bucket.allow_request() is True
    current_time[0] = 1000
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is False

def test_sliding_window_allows_limit():
    current_time[0] = 0
    log = SlidingWindowLog(3,60,fake_clock)
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True

def test_sliding_window_denies_after_limit():
    current_time[0] = 0
    log = SlidingWindowLog(3,60,fake_clock)
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is False

def test_sliding_window_expires_old_requests():
    current_time[0] = 0
    log = SlidingWindowLog(3, 60, fake_clock)
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True
    current_time[0] = 61
    assert log.allow_request() is True

def test_sliding_window_exact_boundary():
    current_time[0] = 0
    log = SlidingWindowLog(3, 60, fake_clock)
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True
    current_time[0] = 60
    assert log.allow_request() is True
