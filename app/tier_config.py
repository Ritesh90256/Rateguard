from app.rate_limit_policy import RateLimitPolicy

tier_config = {
    "free": RateLimitPolicy(
        algorithm = "token_bucket",
        limit = 10,
        window_size = 60,
        capacity = 10,
        refill_rate = 10
    ), 

    "pro": RateLimitPolicy(
        algorithm = "sliding_window_log",
        limit = 100,
        window_size = 60,
        capacity = 100,
        refill_rate = 100
    ),

    "enterprise": RateLimitPolicy(
        algorithm = "sliding_window_counter",
        limit = 1000,
        window_size = 60,
        capacity = 1000,
        refill_rate = 1000
    )
}

client_tiers = {
    "Client-A" : "free",
    "Client-B" : "pro",
    "Client-C" : "enterprise"
}