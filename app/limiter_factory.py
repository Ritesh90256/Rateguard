import time
from app.token_bucket import TokenBucket
from app.sliding_window import SlidingWindowLog
from app.sliding_window_counter import SlidingWindowCounter
from app.rate_limit_policy import RateLimitPolicy

class LimiterFactory:

    def __init__(self, store):
        self.store = store
    
    def create_limiter(self, policy: RateLimitPolicy, client_id):
        if policy.algorithm == "token_bucket":
            return TokenBucket(
                policy.capacity,
                policy.refill_rate,
                time.time,
                self.store,
                client_id
            )

        elif policy.algorithm == "sliding_window_log":
            return SlidingWindowLog(
                policy.limit,
                policy.window_size,
                time.time,
                self.store,
                client_id
            )

        elif policy.algorithm == "sliding_window_counter":
            return SlidingWindowCounter(
                policy.limit,
                policy.window_size,
                time.time,
                self.store,
                client_id
            )

        else:
            raise ValueError(f"unsupported algorithm: {policy.algorithm}")