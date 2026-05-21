
"""Vedic-Enhanced SLM Engine — combines C++ sutra computation with LLM reasoning."""
import json
from backend.core.vedic_kernels_bridge import (
    anurupyena_scale, nikhilam_deficit, paravartya_ph_inversion,
    gunakasamuccaya_wellness, ahimsa_108_stress_code,
    ekadhikena_next_stage, urdhva_yield_score
)
from backend.services.regional_analysis_service import ASSAM_CROP_DATA, PANCHGAVYA_RECIPE

def compute_vedic_grounding(sensor_data, soil_type="loamy", paksha="waxing"):
    """Compute all 8 sutras and return a structured Vedic report."""
    ph, n, p, k, moisture, om, ec, temp = (list(sensor_data) + [6.5]*8)[:8]
    
    # Execute all 8 sutras
    deficit = nikhilam_deficit(n, p, k)
    liming = paravartya_ph_inversion(ph, 6.5)
    ph_score = max(0, 100 - abs(ph - 6.5) * 25)
    npk_score = min(100, (n + p + k) / 1.2)
    moist_score = min(100, moisture * 2)
    om_score = min(100, om * 20)
    wellness = gunakasamuccaya_wellness(ph_score, npk_score, moist_score, om_score)
    stress = ahimsa_108_stress_code(deficit, liming/250.0, 0, wellness)
    n_scale = anurupyena_scale(n, 40.0)
    p_scale = anurupyena_scale(p, 30.0)
    k_scale = anurupyena_scale(k, 40.0)
    yield_idx = urdhva_yield_score(wellness, moist_score, 70, 60)
    
    # Determine best crop based on conditions
    best_crop = "rice"
    if ph < 5.5:
        best_crop = "tea"
    elif moisture < 40:
        best_crop = "mustard"
    elif temp > 32:
        best_crop = "jute"
    
    crop_info = ASSAM_CROP_DATA.get(best_crop, {})
    
    # Build Vedic reasoning report
    report = f"""VEDIC SOIL ANALYSIS (8 Sutras Computed):
1. Anurupyena (Proportionality): N={n_scale:.2f}x, P={p_scale:.2f}x, K={k_scale:.2f}x
2. Nikhilam (Deficit): NPK deficit = {deficit:.1f} ppm below ideal
3. Paravartya (pH Inversion): Liming need = {liming:.0f} kg/ha
4. Gunakasamuccaya (Wellness): Soil health = {wellness:.0f}/100
5. Ahimsa-108 Stress Code: {stress:.0f}/108 (threshold: 75)
6. Ekadhikena (Growth): Next milestone index = {ekadhikena_next_stage(20, 2):.1f}
7. Urdhva-Tiryak (Yield): Estimated yield index = {yield_idx:.0f}/100
8. Shunyam (Balance): {'ACHIEVED' if stress < 10 else 'Needs Panchgavya'}

RECOMMENDED CROP: {best_crop.upper()} ({crop_info.get('season', 'year-round')})
ORGANIC PRACTICES: {', '.join(crop_info.get('organic_practices', ['compost']))}
PAKSHA: {paksha} - {'Good for sowing' if paksha == 'waxing' else 'Good for harvesting'}

AHIMSA-108 PROTOCOL: {'⚠️ CRITICAL — Apply Panchgavya immediately!' if stress >= 75 else '✅ Organic maintenance sufficient'}
Panchgavya recipe: {PANCHGAVYA_RECIPE['ingredients']}"""
    
    return {
        "report": report,
        "wellness": round(wellness, 1),
        "stress_code": round(stress, 1),
        "best_crop": best_crop,
        "yield_index": round(yield_idx, 1),
        "deficit_ppm": round(deficit, 1),
        "liming_kg_ha": round(liming, 1),
        "ahimsa_triggered": stress >= 75,
        "anurupyena_scales": {"N": round(n_scale, 3), "P": round(p_scale, 3), "K": round(k_scale, 3)}
    }


def generate_vedic_prompt(sensor_data, soil_type="loamy", weather_data=None, farmer_query=None):
    """Generate a structured prompt combining Vedic analysis + farmer context."""
    vedic = compute_vedic_grounding(sensor_data, soil_type)
    
    weather_str = ""
    if weather_data:
        temp = weather_data.get('temperature_c', 28)
        rain = weather_data.get('rainfall_mm_monthly', 80)
        weather_str = f"WEATHER: {temp}°C, {rain}mm rainfall this month. "
    
    query_str = f"FARMER ASKS: {farmer_query}" if farmer_query else ""
    
    prompt = f"""{vedic['report']}

{weather_str}
SOIL TYPE: {soil_type}
LOCATION: Silchar, Assam (24.81°N, 92.80°E)
{query_str}

Based on the above Vedic soil analysis (8 sutras computed by C++ kernel), provide:
1. What crop to plant now
2. What organic fertilizer to use (with exact quantity)
3. When to plant (considering moon phase)
4. Any pest/disease warnings
5. Panchgavya application if needed

Answer in simple farmer language. Keep it under 5 sentences."""
    
    return prompt, vedic
