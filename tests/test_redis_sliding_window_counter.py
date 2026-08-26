from app.redis_client import redis_client
from app.redis_store import RedisStore
from app.sliding_window_counter import SlidingWindowCounter


store = RedisStore(redis_client)

current_time = [0]


def fake_clock():
    return current_time[0]

def test_redis_sliding_window_counter_allows_limit():
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

def test_redis_sliding_window_counter_denies_after_limit():
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

def test_redis_sliding_window_counter_weighs_previous_window():
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

def test_redis_sliding_window_counter_uses_weighted_previous_count():
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

def test_redis_sliding_window_counter_resets_after_skipping_windows():
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

def test_redis_sliding_window_counter_shares_state_between_instances():
    current_time[0] = 0

    client_id = "test-counter-shared"
    key = f"rateguard:counter:{client_id}"

    store.delete(key)

    counter_a = SlidingWindowCounter(
        3,
        60,
        fake_clock,
        store,
        client_id
    )

    assert counter_a.allow_request() is True
    assert counter_a.allow_request() is True

    counter_b = SlidingWindowCounter(
        3,
        60,
        fake_clock,
        store,
        client_id
    )

    assert counter_b.allow_request() is True
    assert counter_b.allow_request() is False