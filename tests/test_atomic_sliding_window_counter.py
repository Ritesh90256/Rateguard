from app.redis_store import RedisStore
from app.redis_client import redis_client
from app.sliding_window_counter import SlidingWindowCounter

store = RedisStore(redis_client)

current_time = [0]

def fake_clock():
    return current_time[0]

def test_atomic_sliding_window_allows_limit():
    current_time[0] = 0

    client_id = "test-atomic-counter-basic"
    key = f"rateguard:counter:{client_id}"

    store.delete(key)

    counter = SlidingWindowCounter(3, 60, fake_clock, store, client_id)

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is False

def test_atomic_sliding_window_counter_window_transition():
    current_time[0] = 0

    client_id = "test-atomic-counter-transition"
    key = f"rateguard:counter:{client_id}"

    store.delete(key)

    counter = SlidingWindowCounter(3, 60, fake_clock, store, client_id)

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is False

    current_time[0] = 60

    assert counter.allow_request() is False

def test_atomic_sliding_window_counter_weights_previous_window():
    current_time[0] = 0

    client_id = "test-atomic-counter-weight"
    key = f"rateguard:counter:{client_id}"

    store.delete(key)

    counter = SlidingWindowCounter(5, 60, fake_clock, store, client_id)

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True

    current_time[0] = 90

    assert counter.allow_request() is True

def test_atomic_sliding_window_counter_uses_weighted_previous_count():
    current_time[0] = 0

    client_id = "test-atomic-counter-weighted-decision"
    key = f"rateguard:counter:{client_id}"

    store.delete(key)

    counter = SlidingWindowCounter(3, 60, fake_clock, store, client_id)

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True

    current_time[0] = 60

    assert counter.allow_request() is False

def test_atomic_sliding_window_counter_resets_after_multiple_windows():
    current_time[0] = 0

    client_id = "test-atomic-counter-multiple-windows"
    key = f"rateguard:counter:{client_id}"

    store.delete(key)

    counter = SlidingWindowCounter(3, 60, fake_clock, store, client_id)

    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is True
    assert counter.allow_request() is False

    current_time[0] = 180

    assert counter.allow_request() is True

def test_atomic_sliding_window_counter_persists_state():
    current_time[0] = 0

    client_id = "test-atomic-counter-persistence"
    key = f"rateguard:counter:{client_id}"

    store.delete(key)

    counter = SlidingWindowCounter(3, 60, fake_clock, store, client_id)

    assert counter.allow_request() is True
    assert counter.allow_request() is True

    state = store.get_hash(key)

    assert int(state["previous_count"]) == 0
    assert int(state["current_count"]) == 2
    assert int(float(state["current_fixed_window_start"])) == 0



