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

        state = self.store.get_hash(self.redis_key)

        previous_count = int(state["previous_count"])
        current_count = int(state["current_count"])
        current_fixed_window_start = int(state["current_fixed_window_start"])

        new_fixed_window_start = (current_time // self.window_size) * self.window_size

        gap = new_fixed_window_start - current_fixed_window_start

        if gap == self.window_size:
            previous_count = current_count
            current_count = 0
            current_fixed_window_start = new_fixed_window_start

        elif gap >= 2 * self.window_size:
            previous_count = 0
            current_count = 0
            current_fixed_window_start = new_fixed_window_start

        elapsed_in_current_fixed_window = (
            current_time - current_fixed_window_start
        )

        previous_fixed_window_weight = (
            1 - (elapsed_in_current_fixed_window / self.window_size)
        )

        estimated_count = (
            previous_count * previous_fixed_window_weight
            + current_count
        )

        allowed = False

        if estimated_count < self.limit:
            current_count += 1
            allowed = True

        self.store.set_hash(
            self.redis_key,
            {
                "previous_count": previous_count,
                "current_count": current_count,
                "current_fixed_window_start": current_fixed_window_start,
            }
        )

        return allowed  
