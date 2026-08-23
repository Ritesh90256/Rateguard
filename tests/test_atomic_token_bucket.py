from app.redis_client import redis_client
from app.redis_store import RedisStore
from threading import Thread

store = RedisStore(redis_client)

def test_atomic_token_bucket_allows_limit():
    
    key = ("rateguard:bucket:test-atomic-client")
    capacity = 3
    refill_rate = 10
    current_time = 0

    store.delete(key)

    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1
    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1
    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1
    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 0

def test_atomic_token_bucket_refills():

    key = ("rateguard:bucket:test-atomic-refill")
    capacity = 3
    refill_rate = 10
    current_time = 0

    store.delete(key)

    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1
    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1
    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1

    current_time = 6
    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1

    state = store.get_hash(key)

    assert float(state["tokens"]) == 0.0
    assert float (state["last_updated"]) == 6.0

def test_atomic_token_bucket_never_exceeds_capacity():

    key = ("rateguard:bucket:test-atomic-capacity")
    capacity = 3
    refill_rate = 10
    current_time = 0

    store.delete(key)

    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1

    current_time = 1000

    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1
    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1
    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 1
    assert store.token_bucket_atomic(key,capacity,refill_rate,current_time) == 0

def test_atomic_token_bucket_concurrent_requests():

    results = []
    key = "rateguard:bucket:test-atomic-concurrent"

    store.delete(key)
    store.set_hash(key, {"tokens": 1, "last_updated": 0})

    def make_request():
        result = store.token_bucket_atomic(key,1,10,0)
        results.append(result)

    thread_a = Thread(target= make_request)
    thread_b = Thread(target= make_request)

    thread_a.start()
    thread_b.start()

    thread_a.join()
    thread_b.join()

    assert results.count(1) == 1
    assert results.count(0) == 1


    

    