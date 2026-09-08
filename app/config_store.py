import json
from app.rate_limit_policy import RateLimitPolicy

class ConfigStore:

    def __init__(self, redis_client):
        self.redis = redis_client

    def set_client_tier(self, client_id, tier):
        key = f"rateguard:config:client:{client_id}"

        result = self.redis.set(key, tier)

        self.increment_config_version()

        return result

    def get_client_tier(self, client_id):
        key = f"rateguard:config:client:{client_id}"
        return self.redis.get(key)

    def set_tier_policy(self, tier, policy):
        key = f"rateguard:config:tier:{tier}"

        policy_data = {
            "algorithm" : policy.algorithm,
            "limit" : policy.limit,
            "window_size" : policy.window_size,
            "capacity" : policy.capacity,
            "refill_rate" : policy.refill_rate
        }

        result = self.redis.set(key, json.dumps(policy_data))

        self.increment_config_version()

        return result

    def get_tier_policy(self, tier):
        key = f"rateguard:config:tier:{tier}"

        policy_data = self.redis.get(key)

        if not policy_data:
            return None

        policy_data = json.loads(policy_data)

        return RateLimitPolicy(
            algorithm = policy_data["algorithm"],
            limit = policy_data["limit"],
            window_size = policy_data["window_size"],
            capacity = policy_data["capacity"],
            refill_rate = policy_data["refill_rate"]
        )

    def get_config_version(self):
        key = "rateguard:config:version"

        version = self.redis.get(key)

        if version is None:
            return 0

        return int(version)

    def increment_config_version(self):
        key = "rateguard:config:version"
        return self.redis.incr(key)