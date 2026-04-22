FIXES.md
A complete record of all bugs identified in the provided source code, including file, line number, problem description, and applied fixes.

main.py (FastAPI API Service)
FIX 1 — Hardcoded Redis host breaks in containerized environments

File: main.py
Line: 6

Problem:
Redis connection used `host="localhost"`. In Docker, each service runs in its own container, so `localhost` refers to the container itself, not the Redis service.

Fix:
Replaced with environment variables using `os.getenv()` and defaulted to `redis` (Docker service name).


FIX 2 — Redis connection failures not handled

File: main.py
Lines: 14-17 , 22-27

Problem:
No error handling around Redis operations. Failures caused unhandled exceptions and exposed stack traces.

Fix:
Wrapped Redis operations in `try/except redis.RedisError` and returned `503 Service Unavailable`.


FIX 3 — Incorrect HTTP status for missing job

File: main.py
Line: 25

Problem:
Returned `200 OK` for missing job instead of `404 Not Found`.

Fix:
Used `JSONResponse` with status code `404`.

FIX 4 — Redis responses returned as bytes

File: main.py
Line: 6
Problem:
Redis client returned bytes, requiring manual `.decode()`.

Fix:
Enabled `decode_responses=True` and removed manual decoding.


FIX 5 — Missing health endpoint

File: main.py

Problem:
No `/health` endpoint for Docker and CI/CD health checks.

Fix:
Added `/health` endpoint returning `{"status": "healthy"}`.


FIX 6 — Inconsistent queue naming

File: main.py
Line: 14

Problem:
Used `"job"` for a list storing multiple jobs, causing semantic confusion and fragile coupling with worker.

Fix:
Renamed queue to `"jobs"` for clarity and consistency.


worker.py (Worker Service)

FIX 7 — Hardcoded Redis host

File: worker.py
Line: 6

Problem:
Same Docker networking issue as API.

Fix:
Replaced with environment variables.


FIX 8 — No graceful shutdown handling

File: worker.py
Line: 4 

Problem:
Imported signals but did not implement handlers

Fix:
Implemented signal handlers and graceful shutdown logic.


FIX 9 — No job processing state

File: worker.py
Line: 8-12

Problem:
Jobs remained `"queued"` during processing.

Fix:
Added `"processing"` status before execution.


FIX 10 — No error handling during job processing

File: worker.py
Line: 8-12

Problem:
Failures left jobs stuck and could crash the worker.

Fix:
Wrapped processing in `try/except` and set status to `"failed"` on error.



FIX 11 — Redis responses returned as bytes

File: worker.py

Problem:
Same decoding issue as Main.py.

Fix:
Enabled `decode_responses=True`.


FIX 12 — Queue key mismatch risk

File: worker.py
Line: 16

Problem:
Queue naming relied on implicit matching.

Fix:
Standardized queue name to `"jobs"`.


app.js (Frontend Service)

FIX 13 — Hardcoded API URL breaks container networking
Line: 6
File: app.js

Problem:
Used `localhost`, which fails in Docker.

Fix:
Replaced with `process.env.API_URL || "http://api:8000"`.


FIX 14 — Upstream HTTP status codes not forwarded

File: app.js
Line: 15,23

Problem:
Frontend always returned `200 OK` even when API failed.

Fix:
Forwarded actual status using `res.status(response.status)`.


FIX 15 — Error details swallowed

File: app.js
Line: 17-19, 25-27

Problem:
Catch block returned generic error for all failures.

Fix:
Forwarded upstream error response when available, otherwise returned `502 Bad Gateway`.


FIX 16 — Missing health endpoint

File: app.js

Problem:
No endpoint for container health checks.

Fix:
Added `/health` route returning `{"status": "healthy"}`.


FIX 17 — CRITICAL: Missing Redis dependency in worker requirements

File: worker/requirements.txt

Problem:
Worker service imports redis module on line 1 of worker.py but `redis` is not listed in requirements.txt. This causes ImportError during Docker build and prevents worker from starting.

Fix:
Added `redis` to worker/requirements.txt. Also added `python-dotenv` for environment file support.

Dependencies in requirements.txt: redis, python-dotenv


FIX 18 — Missing API requirements

File: api/requirements.txt

Problem:
Missing optional dependencies like `python-dotenv` for environment variable management.

Fix:
Updated with `fastapi`, `uvicorn[standard]`, `redis`, and `python-dotenv` for complete production readiness.


FIX 19 — Missing Node.js dependencies

File: frontend/package.json

Problem:
Missing `package-lock.json` for Docker build reproducibility.

Fix:
Ensured npm ci is used in Dockerfile for deterministic dependency installation.


Infrastructure & Containerization Fixes

FIX 20 — Empty Dockerfiles

Files: api/Dockerfile, worker/Dockerfile, frontend/Dockerfile

Problem:
All three Dockerfiles were empty, preventing containerization. No multi-stage builds, no health checks, no non-root users, no memory/CPU limits.

Fix:
Created production-grade Dockerfiles with:
- Multi-stage builds to reduce final image size
- Non-root user (UID 1000) for security
- HEALTHCHECK instructions for all services
- No build tools or dev dependencies in final images
- Proper file ownership and permissions


FIX 21 — Missing docker-compose.yml

Problem:
No Docker Compose configuration to orchestrate services, define networking, dependency ordering, or resource limits.

Fix:
Created docker-compose.yml with:
- Named `app-network` for internal service communication
- Redis not exposed on host (internal only)
- Service dependencies with health check conditions
- Environment variables for configuration
- CPU/memory limits (0.5-1 CPU, 256-512 MB RAM per service)
- Proper startup ordering via healthcheck conditions


FIX 22 — Missing .env.example

Problem:
No template for required environment variables, making it unclear what configuration is needed.

Fix:
Created .env.example with placeholders for:
- REDIS_HOST, REDIS_PORT
- API_URL, API_PORT
- FRONTEND_PORT, FRONTEND_API_URL


FIX 23 — Missing .gitignore entry for .env

Problem:
Risk of committing sensitive .env file with real credentials.

Fix:
Ensured .gitignore includes `.env` to prevent accidental commits of sensitive configuration.


FIX 24 — Incomplete API requirements.txt

File: api/requirements.txt

Problem:
uvicorn listed without extras, missing [standard] for full HTTP server capabilities.

Fix:
Updated to `uvicorn[standard]` for production-grade HTTP handling.


FIX 25 — CRITICAL: Redis host defaults prevent local execution

Files: api/main.py (line 10), worker/worker.py (line 8)

Problem:
Default Redis host was hardcoded to `"redis"`, which only resolves inside Docker networks. 
When running locally on Windows/Mac, this causes:
  - getaddrinfo failed
  - Name or service not known
  - Connection refused on redis:6379

The code was: `host=os.getenv("REDIS_HOST", "redis")`

This breaks local development, debugging, and testing outside Docker containers.

Fix:
Changed default from `"redis"` to `"localhost"`:
  - api/main.py line 10: `host=os.getenv("REDIS_HOST", "localhost")`
  - worker/worker.py line 8: `host=os.getenv("REDIS_HOST", "localhost")`

Now works both locally AND in Docker:
- Local: Uses localhost (no env var needed)
- Docker: docker-compose.yml sets REDIS_HOST=redis to override

This enables proper separation of concerns:
✓ Code defaults to local development environment
✓ Deployment configuration overrides via environment variables
✓ Same code works in both contexts
