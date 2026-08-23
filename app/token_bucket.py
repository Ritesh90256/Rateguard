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

        state = self.store.get_hash(self.redis_key)

        tokens = float(state["tokens"])
        last_updated = float(state["last_updated"])

        elapsed_time = current_time - last_updated

        refill_rate_per_sec = self.refill_rate / 60
        tokens_to_fill = elapsed_time * refill_rate_per_sec

        tokens = min(
            self.capacity,
            tokens + tokens_to_fill,
        )

        allowed = False

        if tokens >= 1:
            tokens -= 1
            allowed = True

        self.store.set_hash(
            self.redis_key,
            {
                "tokens": tokens,
                "last_updated": current_time,
            },
        )

        return allowed