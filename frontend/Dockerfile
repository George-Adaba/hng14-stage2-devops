# Stage 1: builder
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .


# Stage 2: runtime
FROM node:18-alpine

WORKDIR /app

RUN adduser -D appuser

# ✅ copy everything from builder
COPY --from=builder /app .

USER appuser

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q -O- http://localhost:3000/health || exit 1

EXPOSE 3000

CMD ["node", "app.js"]