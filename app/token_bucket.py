class TokenBucket:
    def __init__(self, capacity: int, refill_rate : float, clock):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.current_tokens = capacity
        self.clock = clock
        self.start_time = self.clock()

    def allow_request(self):
        current_time = self.clock()
        elapsed_time = current_time - self.start_time
        refill_rate_per_sec = self.refill_rate/60
        tokens_to_fill = elapsed_time * refill_rate_per_sec
        self.current_tokens = min(self.capacity,self.current_tokens + tokens_to_fill)
        self.start_time = current_time

        if self.current_tokens >= 1:
            self.current_tokens -= 1
            return True
        else:
            return False




