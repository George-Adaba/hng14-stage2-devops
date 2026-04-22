HNG 14 Stage 2 DevOps - Job Processing Microservices

A production-ready containerized job processing system with three microservices: frontend, API, and worker, connected via Redis queue.

Prerequisites

Docker (version 20.10+)
Docker Compose (version 1.29+)
Git
Optional:Python 3.11, Node.js 18 for local development

Quick Start

#1. Clone and Setup

bash
git clone <URL>
cd hng14-stage2-devops

Create environment file from template
cp .env.example .env

#2. Start the Full Stack

bash
Build and start all services
docker-compose up --build

Expected output:
 redis        - Ready to accept connections
 api          - Application startup complete
 worker       - Worker ready
 frontend     - Frontend running on port 3000


#3. Accessing the Application

Frontend Dashboard: http://localhost:3000
API Health Check: http://localhost:8000/health
Frontend Health Check: http://localhost:3000/health

#4. Test Job Submission

bash
Submit a job through the API
curl -X POST http://localhost:8000/jobs

Expected response:
{"job_id": "uuid-here"}

Check job status
curl http://localhost:8000/jobs/<job_id>

Expected response (queued):
{"job_id": "uuid-here", "status": "queued"}

After ~2 seconds (completed):
{"job_id": "uuid-here", "status": "completed"}


#5. Stop the Stack

bash
Graceful shutdown
docker-compose down

Remove all data including Redis persistence
docker-compose down -v

Service Details

Frontend (Node.js/Express)
Port: 3000
Endpoints:
GET /health - Health check
POST /submit - Submit new job
GET /status/:id - Get job status
Dependencies: express, axios
Environment: API_URL (default: http://api:8000)

API (Python/FastAPI)
Port: 8000
Endpoints:
GET /health - Health check
POST /jobs - Create new job
GET /jobs/{job_id} - Get job status
Dependencies: fastapi, uvicorn, redis, python-dotenv
Environment: `REDIS_HOST`, `REDIS_PORT`

Worker (Python)
No exposed port
Function: Processes jobs from Redis queue
Status flow: queued → processing → completed (or failed)
Graceful shutdown:** Handles SIGTERM and SIGINT signals
Dependencies: redis, python-dotenv
Environment: `REDIS_HOST`, `REDIS_PORT`

Redis

Port: Not exposed (internal only)
Data: Stored in named volumes for persistence
Health check: `redis-cli ping`

Configuration

All configuration uses environment variables. See `.env.example` for all available options:

env
REDIS_HOST=redis          # Redis service hostname
REDIS_PORT=6379           # Redis service port
API_URL=http://api:8000   # API endpoint for frontend


Important: Never commit `.env` to version control.

Health Checks

All services include HEALTHCHECK instructions:

bash
Check service health status
docker-compose ps

Expected output shows "healthy" for all services:
SERVICE     STATUS
redis       Up 5 seconds (healthy)
api         Up 3 seconds (healthy)
worker      Up 2 seconds (healthy)
frontend    Up 1 second (healthy)


Production Features

Multi-stage Docker builds - Minimal final image sizes (no build tools)  
Non-root user execution - Security hardening (UID 1000)  
Health checks - Every service has HEALTHCHECK instruction  
Resource limits - CPU and memory constraints defined  
No secrets in images - All config via environment variables  
Named networks - Internal service communication  
Dependency ordering - Services wait for dependencies to be healthy  
Graceful shutdown - Workers handle signals properly  

CI/CD Pipeline

The GitHub Actions pipeline runs on every push/PR with these stages:

1. Lint - Python (flake8), JavaScript (eslint), Dockerfiles (hadolint)
2. Test - Pytest with 4+ unit tests, coverage report as artifact
3. Build - Build 3 images, tag with SHA + latest
4. Security Scan - Trivy scan all images, SARIF reports
5. Integration Test - Full stack test with job submission
6. Deploy - Main branch only, rolling update with health checks

To trigger the pipeline, push to main or develop branch or open a PR.

Bug Fixes & Changes

All bugs identified in the starter code have been documented in(FIXES.md).




Development

Local Testing (Without Docker)

bash
Terminal 1: Start Redis
redis-server

Terminal 2: Start API
cd api
pip install -r requirements.txt
uvicorn main:app --reload

Terminal 3: Start Worker
cd worker
pip install -r requirements.txt
python worker.py

Terminal 4: Start Frontend
cd frontend
npm install
npm start




Security Notes
No plaintext secrets in code or config files
`.env` excluded from version control
All services run as non-root user (UID 1000)
Images scanned with Trivy for vulnerabilities
Redis not exposed on host network
Health checks prevent partial deployments

License
Part of Hng14 DevOps Track - Stage 2
