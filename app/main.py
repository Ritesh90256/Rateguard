from fastapi import FastAPI
from pydantic import BaseModel
from app.limiter_factory import LimiterFactory
from app.redis_client import redis_client
from app.redis_store import RedisStore
import os


class CheckRequest(BaseModel):
    client_id: str


algorithm_config = {
    "Client-A": "token_bucket",
    "Client-B": "sliding_window_log",
    "Client-C": "sliding_window_counter"
}


def create_app():
    app = FastAPI()

    app.limiters = {}

    store = RedisStore(redis_client)
    factory = LimiterFactory(store)

    instance_id = os.getenv("INSTANCE_ID", "default")

    @app.post("/check")
    def check_rate_limit(request: CheckRequest):
        if request.client_id not in app.limiters:
            algorithm = algorithm_config.get(request.client_id, "token_bucket")
            limiter = factory.create_limiter(algorithm, request.client_id)

            app.limiters[request.client_id] = limiter

        result = app.limiters[request.client_id].allow_request()

        return {"allowed": result, "instance" : instance_id}

    return app


app = create_app()

limiters = app.limiters