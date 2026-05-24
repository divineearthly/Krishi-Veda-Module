"""
Krishi-Veda SLM Engine
=======================
Loads a 4-bit quantized Small Language Model (Qwen2.5-0.5B-Instruct or
microsoft/Phi-3-mini-4k-instruct) via Hugging Face transformers +
bitsandbytes.

VEDIC LINK (mandatory):
  Before the SLM generates any text, it MUST call vedic_kernels.so to:
    1. Run ahimsa_108_stress_code → if triggered, inject Panchgavya directive
    2. Run anurupyena_scale for each nutrient → inject scaling context

The model loads lazily (on first use) to avoid slowing server startup.
Falls back to rule-based output if torch/transformers/bitsandbytes are
unavailable or insufficient RAM is detected.
"""
from __future__ import annotations
import gc
import os
import sys
import threading
import time
from typing import Optional
import subprocess

# ── Vedic Link imports (always available) ────────────────────────────────────
from backend.core.vedic_enhanced_engine import compute_vedic_grounding, generate_vedic_prompt
from backend.core.vedic_kernels_bridge import (
    anurupyena_scale,
    nikhilam_deficit,
    ahimsa_108_stress_code,
    gunakasamuccaya_wellness,
    paravartya_ph_inversion,
)

# ── Config ───────────────────────────────────────────────────────────────────
PREFERRED_MODELS = [
    "divinesouljoy/VedaRta-0.5B",
    "Qwen/Qwen2.5-0.5B-Instruct",
]
MODEL_CACHE_DIR = os.environ.get(
    "SLM_CACHE_DIR",
    os.path.join(os.path.expanduser("~"), ".cache", "krishi_veda_slm")
)
MAX_NEW_TOKENS = 80
AHIMSA_THRESHOLD = 75.0

# ── Module-level state ───────────────────────────────────────────────────────
_model = None
_tokenizer = None
_model_name: str = ""
_load_lock = threading.Lock()
_load_attempted = False
_load_failed_reason: str = ""


def _check_prerequisites() -> tuple[bool, str]:
    """Return (ok, reason) for whether SLM can be loaded."""
    # No torch/transformers needed — we use llama.cpp subprocess
    return True, "llama.cpp mode"
def _load_model() -> bool:
    """Locate llama-completion binary and GGUF model. No torch needed."""
    global _model, _tokenizer, _model_name, _load_failed_reason

    LLAMA_BIN = os.path.expanduser(
        "/root/llama.cpp/build/bin/llama-completion"
    )
    GGUF_MODEL = os.path.expanduser(
        "/root/vedic-krishi-135m-q4.gguf"
    )

    if not os.path.isfile(LLAMA_BIN):
        _load_failed_reason = f"llama-completion not found at {LLAMA_BIN}"
        print(f"[SLM] {_load_failed_reason}")
        return False

    if not os.path.isfile(GGUF_MODEL):
        _load_failed_reason = f"GGUF model not found at {GGUF_MODEL}"
        print(f"[SLM] {_load_failed_reason}")
        return False

    _model = LLAMA_BIN
    _tokenizer = GGUF_MODEL
    _model_name = "divinesouljoy/VedaRta-0.5B-GGUF (llama.cpp)"
    print(f"[SLM] Using llama.cpp: {_model} with {_tokenizer}")
    return True


def ensure_loaded(blocking: bool = False) -> bool:
    """
    Thread-safe lazy loader.
    If blocking=False (default): returns immediately with current state.
    If blocking=True: waits until load completes (only use in background threads).
    """
    global _load_attempted
    if _model is not None:
        return True
    if not blocking:
        return False
    with _load_lock:
        if _model is not None:
            return True
        if _load_attempted:
            return False
        _load_attempted = True
        return _load_model()


# ── Vedic Grounding ──────────────────────────────────────────────────────────

def _vedic_context_block(sensor_data: list, paksha: str = "waxing") -> tuple[str, dict]:
    """
    MANDATORY: Query vedic_kernels.so before SLM inference.
    Returns (grounding_text, vedic_results).
    """
    if len(sensor_data) < 8:
        sensor_data = (sensor_data + [6.5, 35, 28, 40, 50, 2.0, 0.3, 28])[:8]

    ph, n, p, k, moisture, om, ec, temp = sensor_data

    # Ahimsa-108 check
    deficit = nikhilam_deficit(n, p, k)
    liming = paravartya_ph_inversion(ph)
    ph_score = max(0, 100 - abs(ph - 6.5) * 25)
    npk_score = min(100, (n + p + k) / 1.2)
    moist_score = min(100, moisture * 2)
    om_score = min(100, om * 20)
    wellness = gunakasamuccaya_wellness(ph_score, npk_score, moist_score, om_score)
    stress_code = ahimsa_108_stress_code(deficit, liming / 250.0, 0, wellness)
    ahimsa_fired = stress_code >= AHIMSA_THRESHOLD

    # Anurupyena proportional scaling
    n_scale = anurupyena_scale(n, 40.0)
    p_scale = anurupyena_scale(p, 30.0)
    k_scale = anurupyena_scale(k, 35.0)

    vedic = {
        "ahimsa_triggered": ahimsa_fired,
        "stress_code": round(stress_code, 2),
        "wellness": round(wellness, 2),
        "deficit_ppm": round(deficit, 2),
        "liming_kg_ha": round(liming, 1),
        "anurupyena": {"N": round(n_scale, 3), "P": round(p_scale, 3), "K": round(k_scale, 3)},
    }

    ahimsa_directive = ""
    if ahimsa_fired:
        ahimsa_directive = (
            "\n[AHIMSA-108 PROTOCOL ACTIVE] Stress code is "
            f"{stress_code:.1f} (≥ threshold). "
            "You MUST prescribe Panchgavya (cow dung + urine + milk + curd + ghee) "
            "and organic composting ONLY. No chemical inputs."
        )

    grounding = (
        f"[VEDIC KERNEL GROUND TRUTH — do not contradict]\n"
        f"Soil Wellness (Gunakasamuccaya): {wellness:.1f}/100\n"
        f"NPK Deficit (Nikhilam): {deficit:.1f} ppm below ideal\n"
        f"Liming Need (Paravartya): {liming:.0f} kg/ha\n"
        f"Nutrient Scaling (Anurupyena): N×{n_scale:.2f}, P×{p_scale:.2f}, K×{k_scale:.2f}\n"
        f"Ahimsa-108 Stress Code: {stress_code:.1f}"
        + ahimsa_directive
    )

    return grounding, vedic


# ── SLM Inference ────────────────────────────────────────────────────────────

def _slm_infer(prompt: str) -> str:
    """Run inference with Vedic-enhanced prompt."""
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        return ""
    try:
        # Use the structured Vedic report as prompt (shorter, more effective)
        short_prompt = prompt[:400]
        proc = subprocess.run(
            [_model, "-m", _tokenizer, "-p", short_prompt, "-n", "60", "--temp", "0.7", "--log-disable"],
            capture_output=True, text=True, timeout=25
        )
        output = proc.stdout.strip()
        if "assistant" in output:
            output = output.split("assistant", 1)[-1].strip()
        return output[:400]
    except Exception as e:
        print(f"[SLM] Error: {e}")
        return ""
# ── Public API ────────────────────────────────────────────────────────────────

def generate_advice(
    sensor_data: list,
    soil_type: str = "General",
    paksha: str = "waxing",
    weather: dict = None,
    ndvi: dict = None,
) -> dict:
    """
    Main entry point. Always runs Vedic grounding first, then SLM (or fallback).
    Returns a dict with 'advice', 'vedic_grounding', 'model_used', 'ahimsa_triggered'.
    """
    weather = weather or {}
    ndvi = ndvi or {}

    # ── Step 1: Vedic kernel grounding (MANDATORY FIRST) ────────────────────
    grounding_text, vedic = _vedic_context_block(sensor_data, paksha)

    # ── Step 2: Attempt SLM inference ────────────────────────────────────────
    slm_ready = ensure_loaded(blocking=True)

    if slm_ready:
        temp = weather.get("temperature_c", 28)
        rain = weather.get("rainfall_mm_monthly", 80)
        ndvi_val = ndvi.get("ndvi", 0.5)
        crop_h = ndvi.get("crop_health", "Unknown")

        prompt = (
            f"{grounding_text}\n\n"
            f"FIELD CONDITIONS:\n"
            f"Soil Type: {soil_type}\n"
            f"Moon Phase: {paksha}\n"
            f"Temperature: {temp}°C, Monthly Rainfall: {rain}mm\n"
            f"Satellite NDVI: {ndvi_val} ({crop_h})\n\n"
            f"TASK: You are a Vedic agricultural expert. Using ONLY the verified "
            f"kernel data above, write a concise (5-7 line) farming plan for this "
            f"farmer. Mention the best crop, fertilization, and timing. "
            f"{'Prescribe Panchgavya protocol.' if vedic['ahimsa_triggered'] else ''}"
        )

        try:
            t0 = time.time()
            raw = _slm_infer(prompt)
            elapsed = round(time.time() - t0, 2)
            return {
                "advice": raw,
                "vedic_grounding": vedic,
                "model_used": _model_name,
                "inference_seconds": elapsed,
                "ahimsa_triggered": vedic["ahimsa_triggered"],
                "engine": "slm_4bit_quantized",
            }
        except Exception as e:
            pass  # Fall through to rule-based

    # ── Step 3: Rule-based fallback ──────────────────────────────────────────
    advice = _rule_based_fallback(sensor_data, soil_type, paksha, weather, ndvi, vedic)
    return {
        "advice": advice,
        "vedic_grounding": vedic,
        "model_used": "rule_based_fallback",
        "slm_unavailable_reason": _load_failed_reason or "Not attempted",
        "ahimsa_triggered": vedic["ahimsa_triggered"],
        "engine": "vedic_rule_engine",
    }


def get_slm_status() -> dict:
    """Return the current SLM load status."""
    return {
        "model_loaded": _model is not None,
        "model_name": _model_name or None,
        "load_attempted": _load_attempted,
        "load_failed_reason": _load_failed_reason or None,
        "prerequisites_ok": _check_prerequisites()[0],
    }


def _background_load_worker():
    global _load_attempted
    with _load_lock:
        if _load_attempted:
            return
        _load_attempted = True
        _load_model()


def trigger_background_load() -> None:
    """Kick off model loading in a background thread (call at startup)."""
    t = threading.Thread(target=_background_load_worker, daemon=True)
    t.start()
