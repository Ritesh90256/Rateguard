import time
from app.token_bucket import TokenBucket
from app.sliding_window import SlidingWindowLog
from app.sliding_window_counter import SlidingWindowCounter

class LimiterFactory:

    def __init__(self, store):
        self.store = store
    
    def create_limiter(self, algorithm, client_id):
        if algorithm == "token_bucket":
            return TokenBucket(10,10,time.time, self.store, client_id)
        
        elif algorithm == "sliding_window_log":
            return SlidingWindowLog(10,60,time.time, self.store, client_id)
        
        elif algorithm == "sliding_window_counter":
            return SlidingWindowCounter(10,60, time.time)

        else:
            raise ValueError(f"unsupported algorithm: {algorithm}")
