import time

class TokenBucket:
    def __init__(self, capacity: int, refill_rate : float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.current_tokens = capacity
        self.start_time = time.time()

    def allow_request(self):
        current_time = time.time()
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




