import os
from fastapi import FastAPI
from pydantic import BaseModel
from app.config_store import ConfigStore
from app.limiter_factory import LimiterFactory
from app.logger import log_event
from app.metrics import Metrics, measure_time
from app.redis_client import redis_client
from app.redis_store import RedisStore
from app.tier_config import tier_config

class CheckRequest(BaseModel):
    client_id: str


def create_app():
    app = FastAPI()

    app.limiters = {}
    app.limiter_policies = {}
    app.config_version = 0
    app.metrics = Metrics()

    store = RedisStore(redis_client)
    factory = LimiterFactory(store)
    config_store = ConfigStore(redis_client)

    instance_id = os.getenv("INSTANCE_ID", "default")

    @app.post("/check")
    def check_rate_limit(request: CheckRequest):
        start_time = measure_time()

        try:
            current_config_version = config_store.get_config_version()

            if current_config_version != app.config_version:
                app.config_version = current_config_version
                app.limiters.clear()
                app.limiter_policies.clear()

                log_event(
                    "configuration_reload",
                    instance=instance_id,
                    config_version=current_config_version
                )

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

            latency = measure_time() - start_time

            app.metrics.record_request(
                result,
                latency,
                current_policy.algorithm,
                current_tier
            )

            log_event(
                "rate_limit_decision",
                client_id=request.client_id,
                tier=current_tier,
                algorithm=current_policy.algorithm,
                allowed=result,
                latency_ms=latency * 1000,
                instance=instance_id
            )

            return {
                "allowed": result,
                "instance": instance_id
            }

        except Exception as error:
            latency = measure_time() - start_time

            app.metrics.record_error()

            log_event(
                "request_error",
                client_id=request.client_id,
                error=str(error),
                latency_ms=latency * 1000,
                instance=instance_id
            )

            raise

    @app.get("/metrics")
    def get_metrics():
        return app.metrics.snapshot()

    return app


app = create_app()

limiters = app.limiters