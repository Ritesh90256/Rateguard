from app.token_bucket import TokenBucket
from app.sliding_window import SlidingWindowLog
import time
from app.sliding_window_counter import SlidingWindowCounter

class LimiterFactory:
    
    def create_limiter(self, algorithm):
        if algorithm == "token_bucket":
            return TokenBucket(10,10,time.time)
        
        elif algorithm == "sliding_window_log":
            return SlidingWindowLog(10,60,time.time)
        
        elif algorithm == "sliding_window_counter":
            return SlidingWindowCounter(10,60, time.time)

        else:
            raise ValueError(f"unsupported algorithm: {algorithm}")
