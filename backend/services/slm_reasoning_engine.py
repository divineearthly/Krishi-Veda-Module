"""
SLM Reasoning Engine — Krishi-Veda "Brain"
Implements structured offline reasoning inspired by Phi-3 patterns.
Runs entirely on-device without network calls.

The Ahimsa-108 Protocol is enforced here:
  If stress_code >= 108, all recommendations pivot to Panchgavya / organic composting.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import math
from backend.core.vedic_kernels_bridge import (
    anurupyena_scale, nikhilam_deficit, paravartya_ph_inversion,
    ekadhikena_next_stage, urdhva_yield_score, vilokanam_anomaly,
    gunakasamuccaya_wellness, shunyam_stress_balance, ahimsa_108_stress_code
)


AHIMSA_THRESHOLD = 75.0  # Normalized: 108 sacred units mapped to 75 on the soil stress scale

PANCHGAVYA_PROTOCOL = {
    "primary_intervention": "Panchgavya Application",
    "ingredients": [
        "5L cow dung (fresh)", "3L cow urine (gomuthra)",
        "2L cow milk", "2L curd (dahi)", "500g ghee"
    ],
    "preparation": "Mix all ingredients. Ferment for 7 days stirring twice daily. Dilute 3% before use.",
    "application": "Spray 300L/acre every 15 days during evening hours.",
    "expected_recovery_days": 21,
    "secondary": "Vermicompost at 2 tonnes/acre before next sowing cycle.",
    "vedic_timing": "Apply on Panchami (5th tithi) or Dashami (10th tithi) during waxing moon."
}

ORGANIC_COMPOSTING = {
    "primary_intervention": "Organic Composting",
    "method": "Nadep composting or Vermicomposting",
    "materials": ["Farm waste", "Cow dung", "Neem cake", "Bone meal", "Wood ash"],
    "application_rate": "5 tonnes/hectare, incorporate 3 weeks before sowing",
    "npk_boost": "Gradually restores N:P:K balance over 45-60 days",
    "cost_estimate_inr": 2000
}

CROP_WISDOM = {
    "General": ["Rice", "Wheat", "Maize"],
    "Alluvial": ["Rice", "Sugarcane", "Jute", "Wheat"],
    "Black": ["Cotton", "Soybean", "Jowar", "Wheat"],
    "Red": ["Groundnut", "Millets", "Pulses", "Potato"],
    "Laterite": ["Cashew", "Tapioca", "Tea", "Coffee"],
    "Desert": ["Bajra", "Guar", "Moth bean", "Sesame"],
    "Mountain": ["Apple", "Tea", "Potato", "Barley"]
}

SUTRA_LABELS = {
    "anurupyena": "Anurupyena (Proportionality)",
    "nikhilam": "Nikhilam (Complement Deficit)",
    "paravartya": "Paravartya (pH Inversion)",
    "ekadhikena": "Ekadhikena (Next Growth Stage)",
    "urdhva": "Urdhva-Tiryak (Yield Matrix)",
    "vilokanam": "Vilokanam (Anomaly Detection)",
    "gunakasamuccaya": "Gunakasamuccaya (Wellness Index)",
    "shunyam": "Shunyam (Stress Balance)"
}


@dataclass
class FarmContext:
    lat: float
    lon: float
    sensor_data: List[float]       # [pH, N, P, K, moisture, organic_matter, ec, temp]
    paksha: str = "waxing"
    soil_type: str = "General"
    growth_stage: int = 0
    ndvi: float = 0.5
    rainfall_mm: float = 80.0
    temperature_c: float = 28.0
    historical_npk: List[float] = field(default_factory=list)


@dataclass
class VedicPlan:
    stress_code: float
    ahimsa_triggered: bool
    wellness_score: float
    yield_index: float
    sutra_computations: dict
    primary_crops: List[str]
    recommendations: List[str]
    intervention: Optional[dict]
    next_stage_index: float
    paksha_advice: str
    summary: str
    liming_recommendation_kg_ha: float


def reason(ctx: FarmContext) -> VedicPlan:
    """
    Main reasoning pipeline. Applies all 8 Krishi-Sutras sequentially,
    enforces Ahimsa-108 Protocol, and produces a structured agricultural plan.
    """
    if len(ctx.sensor_data) < 8:
        ctx.sensor_data = (ctx.sensor_data + [6.5, 35.0, 30.0, 35.0, 50.0, 2.0, 0.3, 28.0])[:8]

    ph, n, p, k, moisture, organic_matter, ec, temp = ctx.sensor_data

    # --- Sutra 1: Anurupyena ---
    n_scale = anurupyena_scale(n, 40.0)
    p_scale = anurupyena_scale(p, 30.0)
    k_scale = anurupyena_scale(k, 35.0)
    avg_npk_scale = (n_scale + p_scale + k_scale) / 3.0

    # --- Sutra 2: Nikhilam ---
    deficit = nikhilam_deficit(n, p, k)

    # --- Sutra 3: Paravartya ---
    liming_kg = paravartya_ph_inversion(ph, 6.5)
    ph_score = max(0.0, 100.0 - abs(ph - 6.5) * 25.0)

    # --- Sutra 4: Ekadhikena ---
    current_index = (n + p + k) / 3.0
    next_stage_idx = ekadhikena_next_stage(current_index, ctx.growth_stage)

    # --- Sutra 5: Urdhva-Tiryak ---
    water_index = min(100.0, ctx.rainfall_mm / 2.0 + moisture * 0.5)
    solar_index = min(100.0, max(0.0, ctx.ndvi * 120.0))
    temp_factor = max(0.0, 100.0 - abs(temp - 25.0) * 3.0)
    soil_health_base = min(100.0, (n + p + k) / 1.2)
    yield_idx = urdhva_yield_score(soil_health_base, water_index, solar_index, temp_factor)

    # --- Sutra 6: Vilokanam ---
    history = ctx.historical_npk if ctx.historical_npk else [n, p, k]
    anomaly_flag = vilokanam_anomaly(history)

    # --- Sutra 7: Gunakasamuccaya ---
    npk_score = min(100.0, (n + p + k) / 1.2)
    moisture_score = min(100.0, moisture * 2.0)
    om_score = min(100.0, organic_matter * 20.0)
    wellness = gunakasamuccaya_wellness(ph_score, npk_score, moisture_score, om_score)

    # --- Sutra 8: Shunyam ---
    stress_raw = max(0.0, 100.0 - wellness)
    amendment_potency = min(50.0, organic_matter * 10.0 + (ctx.ndvi * 20.0))
    residual_stress = shunyam_stress_balance(stress_raw, amendment_potency)

    # --- Ahimsa-108 ---
    stress_code = ahimsa_108_stress_code(deficit, liming_kg / 250.0, int(anomaly_flag), wellness)
    ahimsa_triggered = stress_code >= AHIMSA_THRESHOLD

    # --- Build recommendations ---
    recs = []
    intervention = None

    if ahimsa_triggered:
        recs.append(f"⚠️ AHIMSA-108 ALERT: Soil stress code {stress_code:.1f} ≥ 108. Critical intervention needed.")
        recs.append("🐄 Panchgavya application prescribed — Ahimsa-108 Protocol activated.")
        recs.append("🌿 Halt all chemical inputs immediately. Begin organic transition.")
        intervention = {**PANCHGAVYA_PROTOCOL, "stress_code": round(stress_code, 1)}
        if stress_code > 150:
            recs.append("♻️ Supplement with Nadep composting for deep soil restoration.")
            intervention["composting"] = ORGANIC_COMPOSTING
    else:
        if deficit > 20:
            recs.append(f"📉 NPK deficit detected ({deficit:.1f} ppm below ideal). Apply balanced fertilizer.")
        if liming_kg > 100:
            recs.append(f"🪨 pH too acidic. Apply {abs(liming_kg):.0f} kg/ha agricultural lime.")
        elif liming_kg < -100:
            recs.append(f"⚗️ pH too alkaline. Apply {abs(liming_kg):.0f} kg/ha sulfur amendment.")
        if moisture < 30:
            recs.append("💧 Low soil moisture. Irrigate using drip/furrow irrigation.")
        if organic_matter < 1.5:
            recs.append("🌱 Organic matter low. Incorporate green manure or compost before next sowing.")
            intervention = ORGANIC_COMPOSTING
        if anomaly_flag:
            recs.append("🔴 Sensor anomaly detected (Vilokanam). Verify NPK sensor readings.")

    # Paksha-based timing advice
    if ctx.paksha == "waxing":
        paksha_advice = "✨ Shukla Paksha (Waxing Moon): Ideal for sowing, transplanting, and foliar sprays."
    else:
        paksha_advice = "🌑 Krishna Paksha (Waning Moon): Best for harvesting, ploughing, and pest management."

    # Crop selection from regional wisdom
    crops = CROP_WISDOM.get(ctx.soil_type, CROP_WISDOM["General"])

    # Vedic yield optimization
    if yield_idx > 70:
        recs.append(f"🌾 High yield potential ({yield_idx:.0f}/100). {crops[0]} recommended as primary crop.")
    elif yield_idx > 40:
        recs.append(f"🌾 Moderate yield potential ({yield_idx:.0f}/100). Consider {crops[0]} or {crops[1]}.")
    else:
        recs.append(f"🌾 Low yield potential. Soil restoration needed before sowing.")

    recs.append(paksha_advice)

    # Summary sentence
    status = "Critical" if ahimsa_triggered else ("Good" if wellness > 65 else "Moderate")
    summary = (
        f"Soil wellness {wellness:.0f}/100 ({status}). "
        f"Vedic yield index {yield_idx:.0f}/100. "
        f"{'Ahimsa-108 Protocol active — organic intervention required.' if ahimsa_triggered else 'Conventional management advised.'}"
    )

    return VedicPlan(
        stress_code=round(stress_code, 2),
        ahimsa_triggered=ahimsa_triggered,
        wellness_score=round(wellness, 2),
        yield_index=round(yield_idx, 2),
        sutra_computations={
            "anurupyena": {"npk_scale_factors": {"N": round(n_scale, 3), "P": round(p_scale, 3), "K": round(k_scale, 3)}},
            "nikhilam": {"npk_deficit_ppm": round(deficit, 2)},
            "paravartya": {"liming_kg_per_ha": round(liming_kg, 1), "ph_score": round(ph_score, 1)},
            "ekadhikena": {"next_growth_milestone": round(next_stage_idx, 2)},
            "urdhva": {"yield_index": round(yield_idx, 2)},
            "vilokanam": {"anomaly_detected": anomaly_flag},
            "gunakasamuccaya": {"wellness_index": round(wellness, 2)},
            "shunyam": {"residual_stress": round(residual_stress, 2), "shunyam_achieved": residual_stress == 0.0}
        },
        primary_crops=crops,
        recommendations=recs,
        intervention=intervention,
        next_stage_index=round(next_stage_idx, 2),
        paksha_advice=paksha_advice,
        summary=summary,
        liming_recommendation_kg_ha=round(liming_kg, 1)
    )
