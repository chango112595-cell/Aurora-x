# Enable buildx multi-architecture builds
# Supports: linux/amd64, linux/arm64 (Raspberry Pi, Jetson, etc.)
# Optional: --platform=$BUILDPLATFORM

# Aurora-x Docker Container
# Production-ready containerization

FROM node:20-alpine AS base
# Install universal dependencies
RUN apt-get update && apt-get install -y python3 python3-pip pciutils usbutils && rm -rf /var/lib/apt/lists/*
RUN pip3 install psutil fastapi uvicorn

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
# Add Aurora Universal Installer entry
COPY tools/universal_installer.sh /usr/local/bin/aurora-install
RUN chmod +x /usr/local/bin/aurora-install

# Copy Python core
COPY aurora_core.py ./

# Build Next.js
RUN npm run build

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD node -e "require('http').get('http://127.0.0.1:5000/api/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1); })"

# Enable hardware GPU scanning inside container
ENV AURORA_ENABLE_GPU=1

# Start Aurora
CMD ["npm", "start"]
