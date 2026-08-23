from app.rate_limiter import RateLimiter

class TokenBucket(RateLimiter):
    def __init__(self, capacity: int, refill_rate: float, clock, store, client_id):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.clock = clock
        self.store = store
        self.client_id = client_id

        self.redis_key = f"rateguard:bucket:{self.client_id}"

        state = self.store.get_hash(self.redis_key)

        if not state:
            current_time = self.clock()

            self.store.set_hash(
                self.redis_key,
                {
                    "tokens": self.capacity,
                    "last_updated": current_time,
                },
            )

    def allow_request(self):
        current_time = self.clock()

        result = self.store.token_bucket_atomic(
            self.redis_key,
            self.capacity,
            self.refill_rate,
            current_time
        )

        return bool(result)