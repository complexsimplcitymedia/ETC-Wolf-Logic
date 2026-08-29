# syntax=docker/dockerfile:1
FROM python:3.11-slim

LABEL maintainer="Wolf Logic <d_adams1@msn.com>"
LABEL description="Wolf Logic — ETC Eos OSC, MIDI, DMX & High-Dimensional Matrix Engine"

WORKDIR /app

# Install system utilities and audio/ALSA libraries for MIDI
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libasound2-dev \
    libjack-jackd2-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose all lighting & telemetry UDP ports
# 8000: Eos OSC RX, 8001: Eos OSC TX, 9000: Relay Ingest, 6454: Art-Net, 5568: sACN, 58210: TouchOSC MIDI
EXPOSE 8000/udp 8001/udp 9000/udp 6454/udp 5568/udp 58210/udp

# Make scripts executable
RUN chmod +x .agents/skills/etc-osc-bridge/scripts/*.py

# Volume for persistent SQLite database
VOLUME ["/app/data"]

CMD ["python", ".agents/skills/etc-osc-bridge/scripts/eos_realtime_monitor.py", "--port", "9000"]
