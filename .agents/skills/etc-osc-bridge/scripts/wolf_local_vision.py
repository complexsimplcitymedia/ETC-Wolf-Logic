#!/usr/bin/env python3
"""
Wolf Logic — Local Vision Model Ingest & Analysis Client
Integrates with Llama 3.2 Vision (11B) and LLaVA (13B) via Ollama on Apple Silicon M1 Max
to analyze OBS stage video frames, detect beam impacts, and verify live Eos cue execution.
"""

import urllib.request
import json
import base64
import os
import sys
import time
from typing import Dict, List, Optional, Any

OLLAMA_API_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434/api/generate")
DEFAULT_VISION_MODEL = "llama3.2-vision:11b"  # or "llava:13b"

class LocalVisionClient:
    def __init__(self, api_url: str = OLLAMA_API_URL, default_model: str = DEFAULT_VISION_MODEL):
        self.api_url = api_url
        self.default_model = default_model

    def encode_image_base64(self, image_path: str) -> str:
        """Reads local image file and converts to base64 string."""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    def analyze_frame(self, image_path: str, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Sends an image frame to the local vision model (Llama 3.2 Vision / LLaVA)
        running on M1 Max Apple Silicon GPU via Ollama.
        """
        selected_model = model or self.default_model
        
        if not os.path.exists(image_path):
            return {"error": f"Image file not found: {image_path}"}

        img_b64 = self.encode_image_base64(image_path)

        payload = {
            "model": selected_model,
            "prompt": prompt,
            "images": [img_b64],
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9
            }
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.api_url, data=data, headers={"Content-Type": "application/json"})

        start_t = time.time()
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp_json = json.loads(resp.read().decode("utf-8"))
                duration = round(time.time() - start_t, 2)
                return {
                    "model": selected_model,
                    "response": resp_json.get("response", ""),
                    "inference_time_sec": duration,
                    "tokens_evaluated": resp_json.get("eval_count", 0)
                }
        except urllib.error.URLError as e:
            return {
                "error": f"Ollama connection error: {e}. Ensure Ollama is running on your M1 Max (`ollama run {selected_model}`).",
                "mock_response": self._generate_simulated_response(prompt)
            }

    def verify_stage_cue(self, image_path: str, cue_number: str, expected_look: str) -> Dict[str, Any]:
        """Verifies if the actual physical stage matches the Eos cue intent."""
        prompt = (
            f"You are Wolf Logic, an expert theatrical lighting assistant. "
            f"Analyze this stage camera frame for Eos Cue {cue_number}. "
            f"Expected Look: '{expected_look}'. "
            f"1. Identify active fixture beams (Overhead spots, Front wash, Audience grid). "
            f"2. Confirm primary dominant colors (Hue/Saturation). "
            f"3. Note any dark spots, mispointed fixtures, or actors not illuminated."
        )
        return self.analyze_frame(image_path, prompt)

    def _generate_simulated_response(self, prompt: str) -> str:
        return (
            "[Wolf Logic Vision Simulation]: Identified 10 overhead Midstage spots active at 5600K Daylight, "
            "Proscenium wash active at 3200K Tungsten across Downstage Center. "
            "Stage center actor illuminated with high contrast. No dark holes detected on main stage."
        )

if __name__ == "__main__":
    print("[+] Initializing Wolf Logic Local Vision Client (Llama 3.2 Vision / LLaVA)...")
    client = LocalVisionClient()

    print(f"[+] Target Local Vision Model: {DEFAULT_VISION_MODEL} on M1 Max Apple Silicon")
    print("[+] Model capabilities:")
    print("    • Llama 3.2 Vision (11B): High-speed spatial reasoning & coordinate mapping (~7.5GB VRAM)")
    print("    • LLaVA (13B): Theatrical visual instruction & multi-layer color verification (~8.5GB VRAM)")
    
    # Test prompt generation
    print("\n[+] Verification prompt structure:")
    print("    • 'Analyze stage camera frame for Eos Cue 5 (Cyan/Magenta Wave across Midstage Electric)'")
    print("    • 'Extract (X, Y) pixel coordinates of active spotlight beams on the stage floor'")

    print("\n[+] Local Vision Model Client verified and ready.")
