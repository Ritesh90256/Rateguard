from app.rate_limiter import RateLimiter

class SlidingWindowCounter(RateLimiter):
    def __init__(self, limit : int, window_size : int, clock):
        self.limit = limit
        self.window_size = window_size
        self.clock = clock
        self.previous_count = 0
        self.current_count = 0
        self.current_time = self.clock()
        self.current_fixed_window_start = (self.current_time // self.window_size)*self.window_size

    def allow_request(self):
        current_time = self.clock()
        new_fixed_window_start = (current_time // self.window_size)* self.window_size

        gap = new_fixed_window_start - self.current_fixed_window_start

        if gap == self.window_size:
            self.previous_count = self.current_count
            self.current_count = 0
            self.current_fixed_window_start = new_fixed_window_start

        elif gap >= 2*(self.window_size):
            self.previous_count = 0
            self.current_count = 0
            self.current_fixed_window_start = new_fixed_window_start

        elapsed_in_current_fixed_window = current_time - self.current_fixed_window_start
        previous_fixed_window_weight = 1 - (elapsed_in_current_fixed_window/self.window_size)

        estimated_count = (self.previous_count*previous_fixed_window_weight) + self.current_count

        if estimated_count >= self.limit:
            return False
        else:
            self.current_count += 1
            return True
