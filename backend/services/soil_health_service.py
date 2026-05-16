# Soil health analysis service
from backend.core.vedic_kernels_bridge import (
    nikhilam_deficit, paravartya_ph_inversion,
    gunakasamuccaya_wellness, anurupyena_scale
)

def analyze_soil(sensor_data, soil_type="loamy"):
    """Return soil health report using Vedic kernels."""
    ph, n, p, k, moisture, om, ec, temp = (list(sensor_data) + [6.5]*8)[:8]
    ph_score = max(0, 100 - abs(ph - 6.5) * 25)
    npk_score = min(100, (n + p + k) / 1.2)
    moist_score = min(100, moisture * 2)
    om_score = min(100, om * 20)
    wellness = gunakasamuccaya_wellness(ph_score, npk_score, moist_score, om_score)
    deficit = nikhilam_deficit(n, p, k)
    liming = paravartya_ph_inversion(ph, 6.5)
    return {
        "wellness": round(wellness, 1),
        "deficit_ppm": round(deficit, 1),
        "liming_kg_ha": round(liming, 1),
        "ph": ph, "soil_type": soil_type,
        "organic_matter_pct": round(om, 2),
        "recommendation": "organic" if wellness < 50 else "balanced_organic"
    }
