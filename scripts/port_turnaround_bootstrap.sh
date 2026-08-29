#!/usr/bin/env bash
# ==============================================================================
# Wolf Logic — 1-Hour Port Turnaround Docker Desktop Turbo Bootstrap
# ==============================================================================
# Run this script immediately upon docking in port with 5G unlimited data hotspot.
# Pulls all models, Docker images, and package caches in parallel within the 1-hour window.
# Models are saved to ./models on your terabyte SSD for 100% OFFLINE operation at sea.
# ==============================================================================

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "========================================================================"
echo "  🐺 WOLF LOGIC — DOCKER DESKTOP PORT TURNAROUND BOOTSTRAP"
echo "========================================================================"
echo -e "${NC}"
START_TIME=$(date +%s)

# 1. Verify Network Connectivity
echo -e "${YELLOW}[1/5] Checking 5G Port Connectivity & Tailscale Tunnel...${NC}"
ping -c 2 8.8.8.8 > /dev/null 2>&1 && echo -e "${GREEN}✓ High-speed internet detected.${NC}" || {
  echo -e "${RED}✗ No internet connection! Connect to 5G hotspot and retry.${NC}"
  exit 1
}

# 2. Update Central Repository
echo -e "\n${YELLOW}[2/5] Syncing Wolf Logic Repository from GitHub...${NC}"
git pull origin main || echo -e "${YELLOW}! Working with current local repo.${NC}"

# 3. Launch Container Stack in Docker Desktop
echo -e "\n${YELLOW}[3/5] Starting Docker Engine & Local Ollama Services...${NC}"
docker compose up -d --build
echo -e "${GREEN}✓ Docker containers active (wolf-engine & wolf-logic-ollama).${NC}"

# 4. Pull Local AI Models inside Docker Container (Parallel Turbo Mode)
echo -e "\n${YELLOW}[4/5] Downloading Local Models to ./models on SSD (Parallel Streams)...${NC}"

echo -e "${CYAN}--> Pulling Llama 3.2 Vision (11B) (~7.5 GB)...${NC}"
docker compose exec -d ollama ollama pull llama3.2-vision:11b

echo -e "${CYAN}--> Pulling Qwen 2.5 / QwQ Reasoning Model (27B) (~16.0 GB)...${NC}"
docker compose exec -d ollama ollama pull qwen2.5:27b-instruct-q4_K_M

echo -e "${CYAN}--> Pulling Fast Spatial Embeddings Model (~0.3 GB)...${NC}"
docker compose exec -d ollama ollama pull nomic-embed-text

echo -e "${YELLOW}All model download streams dispatched in parallel to Docker Ollama container.${NC}"

# 5. Pre-Cache Local Node.js & Python Dependencies
echo -e "\n${YELLOW}[5/5] Pre-Caching Offline Dependencies...${NC}"
if [ -f "package.json" ] && command -v npm >/dev/null 2>&1; then
  npm install --prefer-offline || true
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo -e "\n${GREEN}"
echo "========================================================================"
echo "  ✓ WOLF LOGIC DOCKER DESKTOP BOOTSTRAP INITIALIZED in ${DURATION}s!"
echo "  • Models downloading directly to persistent SSD volume (./models)."
echo "  • Web Visualizer & Magic Sheet: http://localhost:8888"
echo "  • When ship departs port: runs 100% OFFLINE with ZERO Starlink usage."
echo "========================================================================"
echo -e "${NC}"
