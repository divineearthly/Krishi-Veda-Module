# Sutra parser - translates Vedic sutra names to function calls
from backend.core.vedic_kernels_bridge import (
    anurupyena_scale, nikhilam_deficit, paravartya_ph_inversion,
    ekadhikena_next_stage, urdhva_yield_score, vilokanam_anomaly,
    gunakasamuccaya_wellness, shunyam_stress_balance, ahimsa_108_stress_code
)

SUTRA_MAP = {
    'anurupyena': ('Proportionality', anurupyena_scale),
    'nikhilam': ('All from 9 - Complement', nikhilam_deficit),
    'paravartya': ('Transpose and Adjust', paravartya_ph_inversion),
    'ekadhikena': ('One More Than Previous', ekadhikena_next_stage),
    'urdhva-tiryak': ('Crosswise Multiplication', urdhva_yield_score),
    'vilokanam': ('By Mere Observation', vilokanam_anomaly),
    'gunakasamuccaya': ('Combined Factor', gunakasamuccaya_wellness),
    'shunyam': ('Zero Principle', shunyam_stress_balance),
}

def parse_sutra_instruction(text):
    for name, (desc, func) in SUTRA_MAP.items():
        if name in text.lower():
            return {'sutra': name, 'description': desc, 'function': func.__name__}
    return {'sutra': 'unknown', 'description': 'No Vedic sutra detected'}

def get_all_sutras():
    return {name: desc for name, (desc, _) in SUTRA_MAP.items()}
