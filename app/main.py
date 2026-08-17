from fastapi import FastAPI
from pydantic import BaseModel
from app.token_bucket import TokenBucket

app = FastAPI()

class CheckRequest(BaseModel):
    client_id : str

buckets = {}

@app.post("/check")
def check_rate_limit(request : CheckRequest):
    if request.client_id not in buckets:
        buckets[request.client_id] = TokenBucket(10,10)

    result = buckets[request.client_id].allow_request()

    return {"allowed" : result}



