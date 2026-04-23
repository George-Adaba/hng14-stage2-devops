# Stage 1: builder
FROM python:3.11-alpine AS builder

WORKDIR /app

RUN apk add --no-cache gcc musl-dev

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# Stage 2: runtime
FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache curl

# ✅ correct user creation
RUN adduser -D appuser

# Copy dependencies
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

COPY main.py .

RUN chown -R appuser:appuser /app

USER appuser

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]