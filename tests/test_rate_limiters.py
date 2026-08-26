from app.token_bucket import TokenBucket
from app.sliding_window import SlidingWindowLog
from app.sliding_window_counter import SlidingWindowCounter
from app.redis_client import redis_client
from app.redis_store import RedisStore

store = RedisStore(redis_client)

current_time = [0]
def fake_clock():
    return current_time[0]

def test_token_bucket_allows_limit():
    current_time[0] = 0
    store.delete("rateguard:bucket:test-bucket-limit")
    bucket = TokenBucket(3,10,fake_clock,store,"test-bucket-limit")
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True

def test_token_bucket_denies_after_limit():
    current_time[0] = 0
    store.delete("rateguard:bucket:test-bucket-deny")
    bucket = TokenBucket(3,10,fake_clock,store,"test-bucket-deny")
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is False

def test_token_bucket_refills():
    current_time[0] = 0
    store.delete("rateguard:bucket:test-bucket-refill")
    bucket = TokenBucket(3,10,fake_clock,store,"test-bucket-refill")
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    current_time[0] = 6
    assert bucket.allow_request() is True

def test_token_bucket_never_exceeds_capacity():
    current_time[0] = 0
    store.delete("rateguard:bucket:test-bucket-capacity")
    bucket = TokenBucket(3,10,fake_clock,store,"test-bucket-capacity")
    assert bucket.allow_request() is True
    current_time[0] = 1000
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is True
    assert bucket.allow_request() is False

def test_sliding_window_allows_limit():
    current_time[0] = 0
    store.delete("rateguard:window:test-log-limit")
    log = SlidingWindowLog(3,60,fake_clock, store, "test-log-limit")
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True

def test_sliding_window_denies_after_limit():
    current_time[0] = 0
    store.delete("rateguard:window:test-log-deny")
    log = SlidingWindowLog(3,60,fake_clock, store, "test-log-deny")
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is False

def test_sliding_window_expires_old_requests():
    current_time[0] = 0
    store.delete("rateguard:window:test-log-expire")
    log = SlidingWindowLog(3,60,fake_clock, store, "test-log-expire")
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True
    current_time[0] = 61
    assert log.allow_request() is True

def test_sliding_window_exact_boundary():
    current_time[0] = 0
    store.delete("rateguard:window:test-log-boundary")
    log = SlidingWindowLog(3,60,fake_clock, store, "test-log-boundary")
    assert log.allow_request() is True
    assert log.allow_request() is True
    assert log.allow_request() is True
    current_time[0] = 60
    assert log.allow_request() is True

def test_sliding_window_counter_allows_limit():
    current_time[0] = 0

    client_id = "test-counter-limit"
    key = f"rateguard:counter:{client_id}"
    store.delete(key)

    counter = SlidingWindowCounter(
        3,
        60,
        fake_clock,
        store,
        client_id
    )

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True


def test_sliding_window_counter_denies_after_limit():
    current_time[0] = 0

    client_id = "test-counter-deny"
    key = f"rateguard:counter:{client_id}"
    store.delete(key)

    counter = SlidingWindowCounter(
        3,
        60,
        fake_clock,
        store,
        client_id
    )

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is False


def test_sliding_window_counter_weighs_previous_window():
    current_time[0] = 0

    client_id = "test-counter-weight"
    key = f"rateguard:counter:{client_id}"
    store.delete(key)

    counter = SlidingWindowCounter(
        5,
        60,
        fake_clock,
        store,
        client_id
    )

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True

    current_time[0] = 90

    assert counter.allow_request() is True


def test_sliding_window_counter_uses_weighted_previous_count():
    current_time[0] = 0

    client_id = "test-counter-weighted-decision"
    key = f"rateguard:counter:{client_id}"
    store.delete(key)

    counter = SlidingWindowCounter(
        3,
        60,
        fake_clock,
        store,
        client_id
    )

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True

    current_time[0] = 90

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is False


def test_sliding_window_counter_resets_after_skipping_windows():
    current_time[0] = 0

    client_id = "test-counter-reset"
    key = f"rateguard:counter:{client_id}"
    store.delete(key)

    counter = SlidingWindowCounter(
        3,
        60,
        fake_clock,
        store,
        client_id
    )

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True

    current_time[0] = 120

    assert counter.allow_request() is True






