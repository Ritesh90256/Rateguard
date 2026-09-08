from dataclasses import dataclass

@dataclass
class RateLimitPolicy:
    algorithm: str
    limit: int
    window_size: int
    capacity: int
    refill_rate: float