class RedisStore:
    def __init__(self,redis_client):
        self.redis = redis_client

    def set(self, key, value):
        return self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)