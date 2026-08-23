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