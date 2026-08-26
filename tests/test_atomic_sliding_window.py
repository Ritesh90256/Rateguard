from app.redis_client import redis_client
from app.redis_store import RedisStore
from threading import Thread

store = RedisStore(redis_client)

def test_atomic_sliding_window_allows_limit():
    key = "rateguard:window:test-atomic-sliding"

    store.delete(key)

    limit = 3
    window_ms = 60 * 1000
    current_time_ms = 0

    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-2") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-3") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-4") == 0

def test_atomic_sliding_window_expires_old_requests():
    key = "rateguard:window:test-atomic-sliding-expiry"

    store.delete(key)

    limit = 3
    window_ms = 60 * 1000
    current_time_ms = 0

    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1

    current_time_ms = 61 * 1000

    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1

def test_atomic_sliding_window_exact_boundary():
    key = "rateguard:window:test-atomic-sliding-boundary"

    store.delete(key)

    limit = 3
    window_ms = 60 * 1000
    current_time_ms = 0

    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1

    current_time_ms = 60 * 1000

    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1

def test_atomic_sliding_window_concurrent_requests():
    key = "rateguard:window:test-atomic-sliding-concurrent"

    store.delete(key)

    limit = 2
    window_ms = 60 * 1000
    current_time_ms = 0

    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "initial-request") == 1

    results = []

    def make_request(request_id):
        result = store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, request_id)
        results.append(result)

        thread_a = Thread(target=make_request, args=("request-a"))

        thread_b = Thread(target=make_request, args=("request-b"))

        thread_a.start()
        thread_b.start()

        thread_a.join()
        thread_b.join()

        assert results.count(1) == 1
        assert results.count(0) == 1

def test_atomic_sliding_window_same_timestamp_requests_are_distinct():
    key = "rateguard:window:test-atomic-sliding-same-time"

    store.delete(key)

    limit = 3
    window_ms = 60 * 1000
    current_time_ms = 0

    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-2") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-3") == 1

    state = redis_client.zrange(key, 0, -1, withscores=True)

    assert len(state) == 3
    assert state == [
        ("request-1", 0.0),
        ("request-2", 0.0),
        ("request-3", 0.0),
    ]

def test_atomic_sliding_window_shares_state_between_instances():
    key = "rateguard:window:test-atomic-sliding-shared"

    store.delete(key)

    limit = 3
    window_ms = 60 * 1000
    current_time_ms = 0

    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-2") == 1

    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-3") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-4") == 0

def test_atomic_sliding_window_persists_final_state():
    key = "rateguard:window:test-atomic-sliding-state"

    store.delete(key)

    limit = 3
    window_ms = 60 * 1000
    current_time_ms = 1000

    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-1") == 1
    assert store.sliding_window_log_atomic(key, limit, window_ms, current_time_ms, "request-2") == 1

    state = redis_client.zrange(key, 0, -1, withscores=True)

    assert len(state) == 2
    assert state == [
        ("request-1", 1000.0),
        ("request-2", 1000.0),
    ]

