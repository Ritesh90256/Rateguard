from fastapi import FastAPI
from pydantic import BaseModel
from app.limiter_factory import LimiterFactory
from app.redis_client import redis_client
from app.redis_store import RedisStore
from app.tier_config import tier_config
from app.config_store import ConfigStore
import os

class CheckRequest(BaseModel):
    client_id: str

def create_app():
    app = FastAPI()

    app.limiters = {}
    app.limiter_policies = {}
    app.config_version = 0

    store = RedisStore(redis_client)
    factory = LimiterFactory(store)
    config_store = ConfigStore(redis_client)

    instance_id = os.getenv("INSTANCE_ID", "default")

    @app.post("/check")
    def check_rate_limit(request: CheckRequest):
        current_config_version = config_store.get_config_version()

        if current_config_version != app.config_version:
            app.config_version = current_config_version
            app.limiters.clear()
            app.limiter_policies.clear()
            
        current_tier = config_store.get_client_tier(request.client_id)

        if current_tier is None:
            current_tier = "free"
            config_store.set_client_tier(
                request.client_id,
                current_tier
            )

        current_policy = config_store.get_tier_policy(current_tier)

        if current_policy is None:
            current_policy = tier_config[current_tier]
            config_store.set_tier_policy(
                current_tier,
                current_policy
            )

        cached_policy = app.limiter_policies.get(request.client_id)

        if cached_policy != current_policy:
            limiter = factory.create_limiter(
                current_policy,
                request.client_id
            )

            app.limiters[request.client_id] = limiter
            app.limiter_policies[request.client_id] = current_policy

        result = app.limiters[request.client_id].allow_request()

        return {
            "allowed": result,
            "instance": instance_id
        }

    return app


app = create_app()

limiters = app.limiters