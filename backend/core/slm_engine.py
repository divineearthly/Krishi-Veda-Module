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

# ── Vedic Link imports (always available) ────────────────────────────────────
from backend.core.vedic_kernels_bridge import (
    anurupyena_scale,
    nikhilam_deficit,
    ahimsa_108_stress_code,
    gunakasamuccaya_wellness,
    paravartya_ph_inversion,
)

# ── Config ───────────────────────────────────────────────────────────────────
PREFERRED_MODELS = [
    "Qwen/Qwen2.5-0.5B-Instruct",   # ~500M params, ~350MB 4-bit
    "Qwen/Qwen2-0.5B-Instruct",
    "microsoft/phi-1_5",             # 1.3B params, ~650MB 4-bit
]
MODEL_CACHE_DIR = os.environ.get(
    "SLM_CACHE_DIR",
    os.path.join(os.path.expanduser("~"), ".cache", "krishi_veda_slm")
)
MAX_NEW_TOKENS = 220
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
    try:
        import torch  # noqa: F401
    except ImportError:
        return False, "torch not installed"
    try:
        import transformers  # noqa: F401
    except ImportError:
        return False, "transformers not installed"
    try:
        import psutil
        ram_gb = psutil.virtual_memory().available / 1e9
        if ram_gb < 0.6:
            return False, f"Insufficient RAM: {ram_gb:.1f} GB available"
    except ImportError:
        pass  # psutil optional
    return True, ""


def _load_model() -> bool:
    """Attempt to load the smallest available 4-bit quantized model."""
    global _model, _tokenizer, _model_name, _load_failed_reason

    ok, reason = _check_prerequisites()
    if not ok:
        _load_failed_reason = reason
        return False

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

    bnb_config = None
    try:
        import bitsandbytes  # noqa: F401
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float32,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
    except ImportError:
        pass  # Will load in float32 without quantization

    os.makedirs(MODEL_CACHE_DIR, exist_ok=True)

    for model_id in PREFERRED_MODELS:
        try:
            print(f"[SLM] Attempting to load: {model_id}")
            tokenizer = AutoTokenizer.from_pretrained(
                model_id, cache_dir=MODEL_CACHE_DIR, trust_remote_code=True
            )
            kwargs = dict(
                cache_dir=MODEL_CACHE_DIR,
                device_map="cpu",
                trust_remote_code=True,
                low_cpu_mem_usage=True,
            )
            if bnb_config:
                kwargs["quantization_config"] = bnb_config
            else:
                kwargs["torch_dtype"] = torch.float32

            model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs)
            model.eval()
            _model = model
            _tokenizer = tokenizer
            _model_name = model_id
            print(f"[SLM] Loaded: {model_id}")
            return True
        except Exception as e:
            print(f"[SLM] Failed {model_id}: {e}")
            gc.collect()
            continue

    _load_failed_reason = "All model candidates failed to load"
    return False


def ensure_loaded(blocking: bool = False) -> bool:
    """
    Thread-safe lazy loader.
    If blocking=False (default): returns immediately with current state.
    If blocking=True: waits until load completes (only use in background threads).
    """
    global _load_attempted
    # Fast path: model already loaded
    if _model is not None:
        return True
    # Non-blocking: don't wait for the lock
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
    """Run the loaded SLM synchronously."""
    import torch
    inputs = _tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        out = _model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            temperature=1.0,
            pad_token_id=_tokenizer.eos_token_id,
        )
    full = _tokenizer.decode(out[0], skip_special_tokens=True)
    # Strip the prompt prefix
    answer = full[len(_tokenizer.decode(inputs["input_ids"][0], skip_special_tokens=True)):].strip()
    return answer or full.strip()


def _rule_based_fallback(sensor_data: list, soil_type: str,
                          paksha: str, weather: dict, ndvi: dict,
                          vedic: dict) -> str:
    """Used when SLM model is unavailable."""
    ph = sensor_data[0] if sensor_data else 6.5
    n, p, k = (sensor_data[1:4] + [35, 28, 40])[:3]
    status = "Critical" if vedic["ahimsa_triggered"] else ("Good" if vedic["wellness"] > 65 else "Moderate")
    lines = [
        f"[Rule-Based Reasoning Engine]",
        f"Soil Status: {status} (Wellness {vedic['wellness']:.0f}/100).",
    ]
    if vedic["ahimsa_triggered"]:
        lines += [
            "AHIMSA-108: Critical soil stress detected.",
            "→ Apply Panchgavya: mix 5L cow dung, 3L cow urine, 2L milk, 2L curd, 500g ghee.",
            "→ Ferment 7 days. Spray 3% solution at 300L/acre every 15 days.",
            "→ No chemical fertilizers until wellness exceeds 50.",
        ]
    else:
        if vedic["deficit_ppm"] > 15:
            lines.append(f"→ NPK deficit: {vedic['deficit_ppm']:.1f} ppm. Apply balanced NPK 10-26-26.")
        if vedic["liming_kg_ha"] > 100:
            lines.append(f"→ pH {ph:.1f} too acidic. Apply {vedic['liming_kg_ha']:.0f} kg/ha lime.")
        sc = vedic["anurupyena"]
        lines.append(f"→ Proportional inputs: N×{sc['N']:.2f}, P×{sc['P']:.2f}, K×{sc['K']:.2f}")
    moon = "Shukla Paksha (sow now)" if paksha == "waxing" else "Krishna Paksha (harvest/plough now)"
    lines.append(f"Vedic Timing: {moon}")
    return "\n".join(lines)


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
    slm_ready = ensure_loaded()

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
