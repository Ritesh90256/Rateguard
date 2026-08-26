from app.rate_limiter import RateLimiter
import uuid

class SlidingWindowLog(RateLimiter):
    def __init__(self, limit : int, window_size : int, clock, store, client_id):
        self.limit = limit
        self.window_size = window_size
        self.clock = clock
        self.store = store
        self.client_id = client_id
        self.redis_key = f"rateguard:window:{self.client_id}"

    def allow_request(self):
        current_time_ms = int(self.clock() * 1000)
        window_size_ms = self.window_size * 1000
        request_id = str(uuid.uuid4())

        result = self.store.sliding_window_log_atomic(self.redis_key, self.limit, window_size_ms, current_time_ms, request_id)

        return bool(result)