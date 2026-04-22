from fastapi import FastAPI
from fastapi.responses import JSONResponse
import redis
import uuid
import os

app = FastAPI()

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/jobs")
def create_job():

    try:
        job_id = str(uuid.uuid4())
        r.lpush("jobs", job_id)
        r.hset(f"job:{job_id}", "status", "queued")
        return {"job_id": job_id}
    except redis.RedisError as e:
        return JSONResponse(
            status_code=503,
            content={"error": "Service unavailable", "detail": str(e)}
        )

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        status = r.hget(f"job:{job_id}", "status")
        if not status:
            
            return JSONResponse(
                status_code=404,
                content={"error": "Job not found"}
            )

        return {"job_id": job_id, "status": status}
    except redis.RedisError as e:
        return JSONResponse(
            status_code=503,
            content={"error": "Service unavailable", "detail": str(e)}
        )