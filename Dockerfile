# syntax=docker/dockerfile:1
FROM node:20-slim

LABEL maintainer="Wolf Logic <d_adams1@msn.com>"
LABEL description="Wolf Logic — Universal ETC Eos Ingest, DMX, OSC, HSI Matrix & 3D Magic Sheet Engine"

WORKDIR /app

# Install Python 3, pip, and essential build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up Python virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
COPY package*.json ./
RUN npm install --omit=dev

# Copy application source code
COPY . .

# Expose Web/WebSocket UI (8888) and Lighting UDP Ports (8000, 8001, 9000, 6454, 5568, 58210)
EXPOSE 8888/tcp
EXPOSE 8000/udp 8001/udp 9000/udp 6454/udp 5568/udp 58210/udp

# Volumes for persistent databases and exported CSV streams
VOLUME ["/app/data", "/app/csv_exports"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8888/ || exit 1

# Launch High-Throughput Node.js Ingest & WebSocket Visualizer Engine
CMD ["node", "src/server.js"]
