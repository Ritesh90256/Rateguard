from fastapi import FastAPI
from pydantic import BaseModel
from app.limiter_factory import LimiterFactory
from app.redis_client import redis_client
from app.redis_store import RedisStore
import os
from app.tier_config import tier_config, client_tiers


class CheckRequest(BaseModel):
    client_id: str

def create_app():
    app = FastAPI()

    app.limiters = {}

    store = RedisStore(redis_client)
    factory = LimiterFactory(store)

    instance_id = os.getenv("INSTANCE_ID", "default")

    @app.post("/check")
    def check_rate_limit(request: CheckRequest):
        if request.client_id not in app.limiters:
            tier = client_tiers.get(request.client_id, "free")
            policy = tier_config[tier]

            limiter = factory.create_limiter(policy, request.client_id)
            app.limiters[request.client_id] = limiter

        result = app.limiters[request.client_id].allow_request()

        return {"allowed": result, "instance" : instance_id}

    return app


app = create_app()

limiters = app.limiters