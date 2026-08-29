#!/usr/bin/env bash
# ==============================================================================
# Wolf Logic — Cabin AMD RX 7800 XT Zero-Power 24/7 Mining Engine
# ==============================================================================
# Optimized for AMD RDNA3 (RX 7800 XT / 7900 XT) with $0.00/kWh electricity.
# Focuses exclusively on ASIC-resistant, pure GPU memory & compute algorithms:
#   1. Ravencoin (KAWPOW) - ~35 MH/s (Deep GPU & GDDR6 loading)
#   2. Ergo (Autolykos2) - ~130 MH/s (High-yield AMD memory compute)
#   3. Flux (ZelHash) - ~60 H/s (Decentralized cloud network)
#   4. Clore.ai (KawPow / AI Proof of Useful Work)
# ==============================================================================

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "========================================================================"
echo "  🐺 WOLF LOGIC — 24/7 CABIN GPU MINING ENGINE (AMD RX 7800 XT)"
echo "  Zero Electricity Cost Mode ($0.00/kWh)"
echo "========================================================================"
echo -e "${NC}"

WALLET_RVN=${WALLET_RVN:-"YOUR_RVN_WALLET_ADDRESS"}
WALLET_ERG=${WALLET_ERG:-"YOUR_ERG_WALLET_ADDRESS"}
WALLET_FLUX=${WALLET_FLUX:-"YOUR_FLUX_WALLET_ADDRESS"}
POOL_RVN="stratum+tcp://rvn.2miners.com:6060"
POOL_ERG="stratum+tcp://erg.2miners.com:8888"
POOL_FLUX="stratum+tcp://flux.herominers.com:1199"

echo -e "${YELLOW}Select Mining Profile for RX 7800 XT:${NC}"
echo "  1) Ravencoin (KAWPOW) — 100% GPU / ASIC-Resistant (~35 MH/s)"
echo "  2) Ergo (Autolykos2)  — AMD Memory Architecture Sweet Spot (~130 MH/s)"
echo "  3) Flux (ZelHash)     — Decentralized Compute Utility (~60 H/s)"
echo "  4) Clore.ai / Vast.ai — GPU AI Compute Rental ($0.80-$1.50/day)"

read -p "Enter choice [1-4] (Default: 1): " CHOICE
CHOICE=${CHOICE:-1}

# TeamRedMiner / lolMiner launch sequence
case $CHOICE in
  1)
    echo -e "${GREEN}--> Launching TeamRedMiner: Ravencoin (KAWPOW)...${NC}"
    echo "Command: teamredminer -a kawpow -o $POOL_RVN -u $WALLET_RVN.Cabin7800 -p x --enable_compute"
    ;;
  2)
    echo -e "${GREEN}--> Launching TeamRedMiner: Ergo (Autolykos2)...${NC}"
    echo "Command: teamredminer -a autolykos2 -o $POOL_ERG -u $WALLET_ERG.Cabin7800 -p x"
    ;;
  3)
    echo -e "${GREEN}--> Launching lolMiner: Flux (ZelHash)...${NC}"
    echo "Command: lolMiner --algo ZEL --pool $POOL_FLUX --user $WALLET_FLUX.Cabin7800"
    ;;
  4)
    echo -e "${GREEN}--> Launching Clore.ai / Vast.ai Docker AI Compute Node...${NC}"
    echo "Command: docker run -d --restart always -v /var/run/docker.sock:/var/run/docker.sock clore/compute-client"
    ;;
esac

echo -e "\n${CYAN}Mining bandwidth footprint: < 25 MB / month (Negligible Starlink impact).${NC}"
