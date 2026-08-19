from fastapi import FastAPI
from pydantic import BaseModel
from app.token_bucket import TokenBucket
from app.sliding_window import SlidingWindowLog
import time

app = FastAPI()

class CheckRequest(BaseModel):
    client_id : str

algorithm_config = {
    "Client-A" : "token_bucket",
    "Client-B" : "sliding_window_log"
}

limiters = {}

@app.post("/check")
def check_rate_limit(request : CheckRequest):
    if request.client_id not in limiters:
        algorithm = algorithm_config.get(request.client_id, "token_bucket")
        if algorithm == "token_bucket":
            limiter = TokenBucket(10,10,time.time)
        elif algorithm == "sliding_window_log":
            limiter = SlidingWindowLog(10,60,time.time)

        limiters[request.client_id] = limiter

    result = limiters[request.client_id].allow_request()
    return {"allowed" : result}





