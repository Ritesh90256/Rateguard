from app.redis_client import redis_client
from app.redis_store import RedisStore

def test_redis_store_set_and_get():
    store = RedisStore(redis_client)
    store.set("test:client","hello")
    result = store.get("test:client")
    assert result == "hello"