# Aurora-x Docker Container
# Production-ready containerization

FROM node:20-alpine AS base

# Install Python 3.13
RUN apk add --no-cache python3 py3-pip

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install Node dependencies
RUN npm ci --only=production

# Copy application files
COPY . .

# Copy Python core
COPY aurora_core.py ./

# Build Next.js
RUN npm run build

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD node -e "require('http').get('http://localhost:5000/api/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1); })"

# Start Aurora
CMD ["npm", "start"]
