# Multi-stage build for Frontend service
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production


# Final stage
FROM node:18-alpine

WORKDIR /app

# Create non-root user
RUN addgroup appuser && adduser -S appuser -G appuser

# Copy node modules and app from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --chown=appuser:appuser app.js .
COPY --chown=appuser:appuser views ./views

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q -O- http://localhost:3000/health || exit 1

# Expose port
EXPOSE 3000

# Run application
CMD ["node", "app.js"]
