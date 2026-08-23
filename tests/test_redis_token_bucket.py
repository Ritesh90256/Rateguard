from app.redis_client import redis_client
from app.redis_store import RedisStore
from app.token_bucket import TokenBucket

store = RedisStore(redis_client)

current_time = [0]
def fake_clock():
    return current_time[0]

def test_redis_token_bucket_initializes_state():
    current_time[0] = 0
    store.delete("rateguard:bucket:test-token-client")
    bucket = TokenBucket(3,10,fake_clock,store,"test-token-client")
    state = store.get_hash("rateguard:bucket:test-token-client")
    assert state["tokens"] == "3"
    assert state["last_updated"] == "0"

def test_redis_token_bucket_loads_existing_state():
    current_time[0] = 0
    store.delete("rateguard:bucket:test-token-client")
    store.set_hash("rateguard:bucket:test-token-client", {"tokens": 2, "last_updated": 0})
    bucket = TokenBucket(3,10,fake_clock,store,"test-token-client")
    bucket.allow_request()
    state = store.get_hash("rateguard:bucket:test-token-client")
    assert float(state["tokens"]) == 1.0

def test_redis_token_bucket_shares_states_between_instances():
    current_time[0] = 0
    store.delete("rateguard:bucket:test-token-client")
    bucket_a = TokenBucket(3,10,fake_clock,store,"test-token-client")
    bucket_a.allow_request()
    bucket_b = TokenBucket(3,10,fake_clock,store,"test-token-client")
    bucket_b.allow_request()
    state = store.get_hash("rateguard:bucket:test-token-client")
    assert float(state["tokens"]) == 1.0

def test_redis_token_bucket_refils_from_persisted_timestamp():
    current_time[0] = 0
    store.delete("rateguard:bucket:test-token-client")
    bucket = TokenBucket(3,10,fake_clock,store,"test-token-client")
    bucket.allow_request()
    bucket.allow_request()
    bucket.allow_request()
    current_time[0] = 6
    assert bucket.allow_request() is True
    state = store.get_hash("rateguard:bucket:test-token-client")

    assert float(state["tokens"]) == 0.0
    assert float(state["last_updated"]) == 6.0
