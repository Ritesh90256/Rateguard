class RedisStore:
    def __init__(self,redis_client):
        self.redis = redis_client

    def set(self, key, value):
        return self.redis.set(key, value)

    def get(self, key):
        return self.redis.get(key)

    def set_hash(self, key, mapping):
        self.redis.hset(key, mapping = mapping)

    def get_hash(self, key):
        return self.redis.hgetall(key)

    def delete(self, key):
        return self.redis.delete(key)

    def token_bucket_atomic(self, key, capacity, refill_rate, current_time):
        script = """
            local tokens = redis.call("HGET", KEYS[1], "tokens")
            local last_updated = redis.call("HGET", KEYS[1], "last_updated")
            local capacity = tonumber(ARGV[1])
            local refill_rate = tonumber(ARGV[2])
            local current_time = tonumber(ARGV[3])

            if not tokens then
                tokens = capacity
                last_updated = current_time
                redis.call("HSET", KEYS[1], "tokens", tokens)
                redis.call("HSET", KEYS[1], "last_updated", last_updated)
            end

            tokens = tonumber(tokens)
            last_updated = tonumber(last_updated)

            local elapsed_time = current_time - last_updated
            local refill_rate_per_sec = refill_rate / 60
            local tokens_to_add = elapsed_time * refill_rate_per_sec

            tokens = math.min(capacity, tokens + tokens_to_add)

            local allowed = 0 

            if tokens >= 1 then
                tokens = tokens - 1
                allowed = 1
            end

            redis.call("HSET", KEYS[1], "tokens", tokens, "last_updated", current_time)
            return allowed
            """
        
        result = self.redis.eval(script, 1, key, capacity, refill_rate, current_time)
        return result

    
    def sorted_set_add(self, key, score, member):
        self.redis.zadd(key, {member: score})

    def sorted_set_remove_before(self, key, cutoff):
        return self.redis.zremrangebyscore(key, "-inf", cutoff)

    def sorted_set_count(self, key):
        return self.redis.zcard(key)

    def sliding_window_log_atomic(self, key, limit, window_ms, current_time_ms, request_id):
        script = """
                local limit = tonumber(ARGV[1])
                local window_ms = tonumber(ARGV[2])
                local current_time_ms = tonumber(ARGV[3])
                local request_id = ARGV[4]

                local cutoff = current_time_ms - window_ms
                
                redis.call("ZREMRANGEBYSCORE", KEYS[1], "-inf", cutoff)

                local count = redis.call("ZCARD", KEYS[1])

                if count >= limit then
                    return 0
                end

                redis.call("ZADD", KEYS[1], current_time_ms, request_id)
                return 1

                """

        result = self.redis.eval(script, 1, key, limit, window_ms, current_time_ms, request_id)
        return result

    def sliding_window_counter_atomic(self, key, limit, window_size, current_time):
        script = """
            local previous_count = redis.call("HGET", KEYS[1], "previous_count")
            local current_count = redis.call("HGET", KEYS[1], "current_count")
            local current_fixed_window_start = redis.call("HGET", KEYS[1], "current_fixed_window_start")

            local limit = tonumber(ARGV[1])
            local window_size = tonumber(ARGV[2])
            local current_time = tonumber(ARGV[3])

            if not previous_count then
                previous_count = 0
                current_count = 0

                current_fixed_window_start = math.floor(current_time / window_size) * window_size

                redis.call("HSET",
                KEYS[1],
                "previous_count", previous_count,
                "current_count", current_count,
                "current_fixed_window_start", current_fixed_window_start
                )
            end

            previous_count = tonumber(previous_count)
            current_count = tonumber(current_count)
            current_fixed_window_start = tonumber(current_fixed_window_start)

            local new_fixed_window_start = math.floor(current_time / window_size) * window_size

            local gap = new_fixed_window_start - current_fixed_window_start

            if gap == window_size then
                previous_count = current_count
                current_count = 0
                current_fixed_window_start = new_fixed_window_start

            elseif gap >= 2 * window_size then
                previous_count = 0
                current_count = 0
                current_fixed_window_start = new_fixed_window_start
            end

            local elapsed_in_current_fixed_window = current_time - current_fixed_window_start

            local previous_fixed_window_weight = 1 - (elapsed_in_current_fixed_window / window_size)

            local estimated_count = previous_count * previous_fixed_window_weight + current_count

            local allowed = 0

            if estimated_count < limit then
                current_count = current_count + 1
                allowed = 1
            end

            redis.call(
                "HSET",
                KEYS[1],
                "previous_count", previous_count,
                "current_count", current_count,
                "current_fixed_window_start", current_fixed_window_start
            )

            return allowed

        """

        result = self.redis.eval(script, 1, key, limit, window_size, current_time)

        return result
