# Vedic Sutra execution service
from backend.core.vedic_kernels_bridge import (
    anurupyena_scale, nikhilam_deficit, paravartya_ph_inversion,
    ekadhikena_next_stage, urdhva_yield_score, vilokanam_anomaly,
    gunakasamuccaya_wellness, shunyam_stress_balance, ahimsa_108_stress_code
)

SUTRAS = {
    "anurupyena": anurupyena_scale,
    "nikhilam": nikhilam_deficit,
    "paravartya": paravartya_ph_inversion,
    "ekadhikena": ekadhikena_next_stage,
    "urdhva": urdhva_yield_score,
    "vilokanam": vilokanam_anomaly,
    "gunakasamuccaya": gunakasamuccaya_wellness,
    "shunyam": shunyam_stress_balance,
}

def execute_sutra(name, *args, **kwargs):
    """Execute a named Vedic sutra with given arguments."""
    if name in SUTRAS:
        return SUTRAS[name](*args, **kwargs)
    raise ValueError(f"Unknown sutra: {name}. Available: {list(SUTRAS.keys())}")

def run_all_sutras(sensor_data):
    """Run all 8 sutras on sensor data and return results dict."""
    ph, n, p, k, moisture, om, ec, temp = (list(sensor_data) + [6.5]*8)[:8]
    deficit = nikhilam_deficit(n, p, k)
    liming = paravartya_ph_inversion(ph, 6.5)
    ph_score = max(0, 100 - abs(ph - 6.5) * 25)
    npk_score = min(100, (n + p + k) / 1.2)
    moist_score = min(100, moisture * 2)
    om_score = min(100, om * 20)
    wellness = gunakasamuccaya_wellness(ph_score, npk_score, moist_score, om_score)
    return {
        "anurupyena_n": anurupyena_scale(n, 40.0),
        "nikhilam_deficit": deficit,
        "paravartya_liming": liming,
        "gunakasamuccaya_wellness": wellness,
        "ahimsa_108": ahimsa_108_stress_code(deficit, liming/250.0, 0, wellness)
    }
