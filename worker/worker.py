import redis
import time
import os
import signal
import sys
 
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)
 
shutdown = False
 
 
def handle_signal(signum, frame):
    global shutdown
    print("Shutdown signal received. Finishing current job before stopping...")
    shutdown = True
 
 
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)
 
 
def process_job(job_id):
    print(f"Processing job {job_id}")
 
    r.hset(f"job:{job_id}", "status", "processing")
 
    try:
        time.sleep(2)  # simulate work
        r.hset(f"job:{job_id}", "status", "completed")
        print(f"Done: {job_id}")
    except Exception as e:
        r.hset(f"job:{job_id}", "status", "failed")
        print(f"Job {job_id} failed: {e}")
 
 
while not shutdown:
    job = r.brpop("jobs", timeout=5)
    if job:
        _, job_id = job
        process_job(job_id)
 
print("Worker shut down cleanly.")
sys.exit(0)

