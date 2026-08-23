class RedisStore:
    def __init__(self,redis_client):
        self.redis = redis_client

    def set(self, key, value):
        return self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)

    def set_hash(self, key, mapping):
        self.redis.hset(key, mapping = mapping)

    def get_hash(self, key):
        return self.redis.hgetall(key)

    def delete(self, key):
        return self.redis.delete(key)

