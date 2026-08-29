#!/usr/bin/env bash
# ==============================================================================
# Wolf Logic — Direct High-Speed Model Downloader to 256GB Card
# ==============================================================================
# Downloads Llama 3.2 Vision (11B), Qwen 2.5 / QwQ (27B), and Nomic Embeddings
# directly onto your external 256GB drive so you never touch cell data or Starlink.
# ==============================================================================

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TARGET_DIR="/mnt/wolf-thumb/models"
mkdir -p "$TARGET_DIR"

echo -e "${CYAN}"
echo "========================================================================"
echo "  🐺 WOLF LOGIC — GIGABIT MODEL PRE-DOWNLOADER TO 256GB DRIVE"
echo "  Target Storage Path: $TARGET_DIR"
echo "========================================================================"
echo -e "${NC}"

# Check available disk space
AVAILABLE_GB=$(df -BG "$TARGET_DIR" | awk 'NR==2 {print $4}' | sed 's/G//')
echo -e "${YELLOW}[+] Available Storage on Drive: ${AVAILABLE_GB} GB${NC}"

# 1. Download Qwen 2.5 27B Instruct (Q4_K_M GGUF) (~16.5 GB)
QWEN_URL="https://huggingface.co/Qwen/Qwen2.5-27B-Instruct-GGUF/resolve/main/qwen2.5-27b-instruct-q4_k_m.gguf"
QWEN_FILE="$TARGET_DIR/qwen2.5-27b-instruct-q4_k_m.gguf"

echo -e "\n${CYAN}[1/3] Downloading Qwen 2.5 27B Instruct Q4_K_M (~16.5 GB)...${NC}"
if [ -f "$QWEN_FILE" ]; then
  echo -e "${GREEN}✓ Qwen 2.5 27B already exists on drive.${NC}"
else
  curl -L -C - --progress-bar "$QWEN_URL" -o "$QWEN_FILE"
  echo -e "${GREEN}✓ Qwen 2.5 27B downloaded successfully.${NC}"
fi

# 2. Download Llama 3.2 Vision 11B GGUF (~7.5 GB)
LLAMA_VISION_URL="https://huggingface.co/bartowski/Llama-3.2-11B-Vision-Instruct-GGUF/resolve/main/Llama-3.2-11B-Vision-Instruct-Q4_K_M.gguf"
LLAMA_VISION_FILE="$TARGET_DIR/Llama-3.2-11B-Vision-Instruct-Q4_K_M.gguf"

echo -e "\n${CYAN}[2/3] Downloading Llama 3.2 Vision 11B Q4_K_M (~7.5 GB)...${NC}"
if [ -f "$LLAMA_VISION_FILE" ]; then
  echo -e "${GREEN}✓ Llama 3.2 Vision already exists on drive.${NC}"
else
  curl -L -C - --progress-bar "$LLAMA_VISION_URL" -o "$LLAMA_VISION_FILE"
  echo -e "${GREEN}✓ Llama 3.2 Vision downloaded successfully.${NC}"
fi

# 3. Download Nomic Spatial Embeddings (~0.3 GB)
EMBED_URL="https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.Q8_0.gguf"
EMBED_FILE="$TARGET_DIR/nomic-embed-text-v1.5.Q8_0.gguf"

echo -e "\n${CYAN}[3/3] Downloading Nomic Embed Text v1.5 Q8 (~0.3 GB)...${NC}"
if [ -f "$EMBED_FILE" ]; then
  echo -e "${GREEN}✓ Nomic Embeddings already exists on drive.${NC}"
else
  curl -L -C - --progress-bar "$EMBED_URL" -o "$EMBED_FILE"
  echo -e "${GREEN}✓ Nomic Embeddings downloaded successfully.${NC}"
fi

# Create Modelfiles for Instant 1-Click Import into Ollama
cat <<EOF > "$TARGET_DIR/Modelfile.qwen27b"
FROM $QWEN_FILE
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER stop "<|im_end|>"
SYSTEM You are Wolf Logic, an expert theatrical lighting assistant and master ETC Eos console programmer.
EOF

cat <<EOF > "$TARGET_DIR/Modelfile.llama_vision"
FROM $LLAMA_VISION_FILE
PARAMETER temperature 0.2
SYSTEM You are Wolf Logic Vision, analyzing stage camera frames and fixture beam impact coordinates.
EOF

echo -e "\n${GREEN}"
echo "========================================================================"
echo "  ✓ ALL MASTER MODELS PRE-CACHED ON 256GB DRIVE!"
echo "  • Total Size: ~24.3 GB (Stored in /mnt/wolf-thumb/models)"
echo "  • When you plug into your MacBook: run 'ollama create qwen27b -f /path/to/Modelfile.qwen27b'"
echo "  • ZERO cellular or satellite data will ever be needed."
echo "========================================================================"
echo -e "${NC}"
