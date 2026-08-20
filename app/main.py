from fastapi import FastAPI
from pydantic import BaseModel
from app.limiter_factory import LimiterFactory

app = FastAPI()

class CheckRequest(BaseModel):
    client_id : str

algorithm_config = {
    "Client-A" : "token_bucket",
    "Client-B" : "sliding_window_log"
}

limiters = {}
factory = LimiterFactory()

@app.post("/check")
def check_rate_limit(request : CheckRequest):
    if request.client_id not in limiters:
        algorithm = algorithm_config.get(request.client_id, "token_bucket")
        limiter = factory.create_limiter(algorithm)

        limiters[request.client_id] = limiter

    result = limiters[request.client_id].allow_request()
    return {"allowed" : result}





