from app.rate_limiter import RateLimiter

class SlidingWindowCounter(RateLimiter):
    def __init__(self, limit : int, window_size : int, clock, store, client_id):
        self.limit = limit
        self.window_size = window_size
        self.clock = clock
        self.store = store
        self.client_id = client_id
        self.redis_key = f"rateguard:counter:{self.client_id}"
        state = self.store.get_hash(self.redis_key)

        if not state:
            current_time = self.clock()

            current_fixed_window_start = int((current_time // self.window_size)*self.window_size)

            self.store.set_hash(
                self.redis_key,
                {
                    "previous_count" : 0,
                    "current_count" : 0,
                    "current_fixed_window_start" : current_fixed_window_start
                }
            )

        else:
            self.previous_count = int(state["previous_count"])
            self.current_count = int(state["current_count"])
            self.current_fixed_window_start = int(float(state["current_fixed_window_start"]))

    def allow_request(self):
        current_time = self.clock()

        result = self.store.sliding_window_counter_atomic(self.redis_key, self.limit, self.window_size, current_time)

        return bool(result)
