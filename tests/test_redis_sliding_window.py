from app.redis_client import redis_client
from app.redis_store import RedisStore
from app.sliding_window import SlidingWindowLog

store = RedisStore(redis_client)
current_time  = [0]

def fake_clock():
    return current_time[0]

def test_redis_sliding_window_allows_limit():
    current_time[0] = 0
    client_id = "test-sliding-window-limit"
    key = f"rateguard:window:{client_id}"

    store.delete(key)

    log = SlidingWindowLog(3, 60, fake_clock, store, client_id)

    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True

def test_redis_sliding_window_denies_after_limit():
    current_time[0] = 0
    client_id = "test-sliding-window-deny"
    key = f"rateguard:window:{client_id}"

    store.delete(key)

    log = SlidingWindowLog(3, 60, fake_clock, store, client_id)

    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is False

def test_redis_sliding_window_expires_old_requests():
    current_time[0] = 0
    client_id = "test-sliding-window-expire"
    key = f"rateguard:window:{client_id}"

    store.delete(key)

    log = SlidingWindowLog(3, 60, fake_clock, store, client_id)

    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True

    current_time[0] = 61

    assert log.allow_request() is True

def test_redis_sliding_window_exact_boundary():
    current_time[0] = 0
    client_id = "test-sliding-window-boundary"
    key = f"rateguard:window:{client_id}"

    store.delete(key)

    log = SlidingWindowLog(3, 60, fake_clock, store, client_id)

    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True

    current_time[0] = 60

    assert log.allow_request() is True

def test_redis_sliding_window_shares_state_between_instances():
    current_time[0] = 0
    client_id = "test-sliding-window-shared"
    key = f"rateguard:window:{client_id}"

    store.delete(key)

    log_a = SlidingWindowLog(3, 60, fake_clock, store, client_id)
    assert log_a.allow_request() is True
    assert log_a.allow_request() is True

    log_b = SlidingWindowLog(3, 60, fake_clock, store, client_id)
    assert log_b.allow_request() is True
    assert log_b.allow_request() is False
