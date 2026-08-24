from app.redis_client import redis_client
from app.redis_store import RedisStore

def test_redis_store_set_and_get():
    store = RedisStore(redis_client)
    store.set("test:client","hello")
    result = store.get("test:client")
    assert result == "hello"

def test_redis_store_hash_set_and_hash_get():
    store = RedisStore(redis_client)
    store.set_hash("test:bucket",{"tokens":7.5, "last_updated":12345})
    result = store.get_hash("test:bucket")
    assert result == {"tokens":"7.5", "last_updated":"12345"}

def test_redis_store_sorted_set_add():
    key = "test:window"
    store = RedisStore(redis_client)
    store.delete(key)
    store.sorted_set_add(key, 100123, "request-1")
    result = redis_client.zrange(key,0,-1, withscores=True)
    assert result == [("request-1", 100123.0)]

def test_redis_store_sorted_set_remove_before():
    key = "test:window:remove"
    store = RedisStore(redis_client)
    store.delete(key)

    store.sorted_set_add(key, 100, "request-1")
    store.sorted_set_add(key, 105, "request-2")
    store.sorted_set_add(key, 110, "request-3")

    store.sorted_set_remove_before(key, 105)
    result = redis_client.zrange(key, 0, -1, withscores=True)

    assert result == [("request-3", 110.0)]

def test_redis_store_sorted_set_count():
    key = "test:window:count"
    store = RedisStore(redis_client)
    store.delete(key)

    store.sorted_set_add(key, 100, "request-1")
    store.sorted_set_add(key, 105, "request-2")
    store.sorted_set_add(key, 110, "request-3")

    result = store.sorted_set_count(key)
    assert result == 3