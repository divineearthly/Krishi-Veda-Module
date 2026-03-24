"""
Vedic Kernels Bridge
Loads vedic_kernels.so and exposes all 8 Krishi-Sutras as Python functions.
Falls back gracefully if the shared library is not available.
"""
import ctypes
import os
import math

_LIB_PATH = os.path.join(
    os.path.dirname(__file__), "../../vedic_engine/kernels/vedic_kernels.so"
)
_lib = None


def _load():
    global _lib
    if _lib is not None:
        return _lib
    try:
        lib = ctypes.CDLL(os.path.abspath(_LIB_PATH))

        # 1. Anurupyena
        lib.anurupyena_scale.restype = ctypes.c_double
        lib.anurupyena_scale.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

        # 2. Nikhilam
        lib.nikhilam_deficit.restype = ctypes.c_double
        lib.nikhilam_deficit.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]

        # 3. Paravartya
        lib.paravartya_ph_inversion.restype = ctypes.c_double
        lib.paravartya_ph_inversion.argtypes = [ctypes.c_double, ctypes.c_double]

        # 4. Ekadhikena
        lib.ekadhikena_next_stage.restype = ctypes.c_double
        lib.ekadhikena_next_stage.argtypes = [ctypes.c_double, ctypes.c_int]

        # 5. Urdhva-Tiryak
        lib.urdhva_yield_score.restype = ctypes.c_double
        lib.urdhva_yield_score.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double
        ]

        # 6. Vilokanam
        lib.vilokanam_anomaly.restype = ctypes.c_int
        lib.vilokanam_anomaly.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_double
        ]

        # 7. Gunakasamuccaya
        lib.gunakasamuccaya_wellness.restype = ctypes.c_double
        lib.gunakasamuccaya_wellness.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double
        ]

        # 8. Shunyam
        lib.shunyam_stress_balance.restype = ctypes.c_double
        lib.shunyam_stress_balance.argtypes = [ctypes.c_double, ctypes.c_double]

        # Ahimsa-108
        lib.ahimsa_108_stress_code.restype = ctypes.c_double
        lib.ahimsa_108_stress_code.argtypes = [
            ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double
        ]

        _lib = lib
    except Exception as e:
        print(f"[VedicKernels] Could not load .so: {e}. Using Python fallback.")
        _lib = False
    return _lib


def anurupyena_scale(observed: float, ideal_ref: float, tolerance: float = 0.1) -> float:
    lib = _load()
    if lib:
        return lib.anurupyena_scale(observed, ideal_ref, tolerance)
    if ideal_ref <= 0:
        return 1.0
    ratio = observed / ideal_ref
    return max(0.1, min(2.0, 1.0 - 0.5 * (ratio - 1.0)))


def nikhilam_deficit(n: float, p: float, k: float) -> float:
    lib = _load()
    if lib:
        return lib.nikhilam_deficit(n, p, k)
    base = 40.0
    return ((base - min(n, base)) + (base - min(p, base)) + (base - min(k, base))) / 3.0


def paravartya_ph_inversion(ph: float, target_ph: float = 6.5) -> float:
    lib = _load()
    if lib:
        return lib.paravartya_ph_inversion(ph, target_ph)
    return -(ph - target_ph) * 250.0


def ekadhikena_next_stage(current_index: float, growth_stage: int) -> float:
    lib = _load()
    if lib:
        return lib.ekadhikena_next_stage(current_index, growth_stage)
    increments = [1.0, 1.618, 2.618, 4.236, 6.854, 11.09, 17.94, 29.03]
    return current_index + increments[min(growth_stage, 7)]


def urdhva_yield_score(soil: float, water: float, solar: float, temp: float) -> float:
    lib = _load()
    if lib:
        return lib.urdhva_yield_score(soil, water, solar, temp)
    cross1 = soil * water
    cross2 = solar * temp
    vertical = soil * solar + water * temp
    return min(100.0, (cross1 + cross2 + vertical) / 30000.0 * 100.0)


def vilokanam_anomaly(values: list, threshold_sigma: float = 2.0) -> bool:
    lib = _load()
    if lib and len(values) >= 2:
        arr = (ctypes.c_double * len(values))(*values)
        return bool(lib.vilokanam_anomaly(arr, len(values), threshold_sigma))
    if len(values) < 2:
        return False
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(var) if var > 0 else 0
    return abs(values[-1] - mean) > threshold_sigma * std if std > 0 else False


def gunakasamuccaya_wellness(ph_s: float, npk_s: float, moist_s: float, om_s: float) -> float:
    lib = _load()
    if lib:
        return lib.gunakasamuccaya_wellness(ph_s, npk_s, moist_s, om_s)
    product = ph_s * npk_s * moist_s * om_s
    return min(100.0, max(0.0001, product) ** 0.25)


def shunyam_stress_balance(stress: float, amendment: float) -> float:
    lib = _load()
    if lib:
        return lib.shunyam_stress_balance(stress, amendment)
    residual = stress - amendment
    return 0.0 if abs(residual) < 1.0 else residual


def ahimsa_108_stress_code(nikhilam_d: float, paravartya_d: float,
                            vilokanam_flag: int, wellness: float) -> float:
    lib = _load()
    if lib:
        return lib.ahimsa_108_stress_code(nikhilam_d, paravartya_d, vilokanam_flag, wellness)
    base = (nikhilam_d / 40.0) * 60.0
    return base + abs(paravartya_d) * 2.0 + vilokanam_flag * 20.0 + (100.0 - wellness) * 0.3
