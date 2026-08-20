from app.rate_limiter import RateLimiter

class SlidingWindowLog(RateLimiter):
    def __init__(self, limit : int, window_size : int, clock):
        self.limit = limit
        self.window_size = window_size
        self.timestamps = []
        self.clock = clock

    def allow_request(self):
        current_time = self.clock()
        remaining_timestamps = []
        start_window = current_time - self.window_size
        for timestamp in self.timestamps:
            if timestamp > start_window:
                remaining_timestamps.append(timestamp)

        self.timestamps = remaining_timestamps

        if len(self.timestamps) >= self.limit :
            return False
        else:
            self.timestamps.append(current_time)
            return True
