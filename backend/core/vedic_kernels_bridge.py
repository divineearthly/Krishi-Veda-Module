"""
Vedic Kernels Bridge — Production Version
Loads compiled Urdhva Tiryagbhyam kernels from vedic_kernels.so
Includes: Urdhva MatMul, Nikhilam Softmax, Shunyam Norm, Ekadhikena Position
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
        
        # Urdhva Tiryagbhyam — Matrix Multiplication
        lib.urdhva_matmul.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int
        ]
        lib.urdhva_matmul.restype = None
        
        # Nikhilam Softmax
        lib.nikhilam_softmax.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int
        ]
        lib.nikhilam_softmax.restype = None
        
        # Shunyam Layer Normalization
        lib.shunyam_norm.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int
        ]
        lib.shunyam_norm.restype = None
        
        # Ekadhikena Position Encoding
        lib.ekadhikena_position.argtypes = [
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_int,
            ctypes.c_int
        ]
        lib.ekadhikena_position.restype = None
        
        _lib = lib
        print("[VedicKernels] ✅ Native .so loaded — Urdhva, Nikhilam, Shunyam, Ekadhikena active")
    except Exception as e:
        print(f"[VedicKernels] .so not found ({e}). Using Python fallback.")
        _lib = False
    return _lib


# ── Public API — mirrors original bridge interface ─────────────────────────

def urdhva_matmul(A, B, C, N):
    """Urdhva Tiryagbhyam matrix multiply. A,B,C are flat float lists of size N*N."""
    lib = _load()
    if lib:
        A_arr = (ctypes.c_float * (N*N))(*A)
        B_arr = (ctypes.c_float * (N*N))(*B)
        C_arr = (ctypes.c_float * (N*N))()
        lib.urdhva_matmul(A_arr, B_arr, C_arr, N)
        return list(C_arr)
    # Python fallback — blocked multiply
    C = [0.0] * (N*N)
    for i in range(0, N, 4):
        for j in range(0, N, 4):
            for k in range(0, N, 4):
                for ii in range(i, min(i+4, N)):
                    for jj in range(j, min(j+4, N)):
                        s = 0.0
                        for kk in range(k, min(k+4, N)):
                            s += A[ii*N + kk] * B[kk*N + jj]
                        C[ii*N + jj] += s
    return C

def nikhilam_softmax(x):
    """Nikhilam-based softmax approximation."""
    lib = _load()
    n = len(x)
    if lib:
        arr = (ctypes.c_float * n)(*x)
        lib.nikhilam_softmax(arr, n)
        return list(arr)
    # Python fallback
    max_val = max(x)
    exp_vals = [(1.0 + (v - max_val) * 0.25) ** 4 for v in x]
    exp_vals = [max(v, 0.001) for v in exp_vals]
    s = sum(exp_vals)
    return [v / s for v in exp_vals]

def shunyam_norm(x):
    """Shunyam zero-centering normalization."""
    lib = _load()
    n = len(x)
    if lib:
        arr = (ctypes.c_float * n)(*x)
        lib.shunyam_norm(arr, n)
        return list(arr)
    mean = sum(x) / n
    centered = [v - mean for v in x]
    std = math.sqrt(sum(v*v for v in centered) / n + 1e-5)
    return [v / std for v in centered]

def ekadhikena_position(seq_len, dim):
    """Ekadhikena Purvena position encoding — golden ratio based."""
    lib = _load()
    n = seq_len * dim
    if lib:
        arr = (ctypes.c_float * n)()
        lib.ekadhikena_position(arr, seq_len, dim)
        return list(arr)
    phi = 1.618033988749895
    result = []
    for pos in range(seq_len):
        for d in range(dim):
            if d % 2 == 0:
                result.append(math.sin(pos / (phi ** (d / dim))))
            else:
                result.append(math.cos(pos / (phi ** ((d-1) / dim))))
    return result


# ── Original Krishi Sutras (unchanged) ──────────────────────────────────────

def anurupyena_scale(observed, ideal_ref, tolerance=0.1):
    if ideal_ref <= 0: return 1.0
    ratio = observed / ideal_ref
    return max(0.1, min(2.0, 1.0 - 0.5 * (ratio - 1.0)))

def nikhilam_deficit(n, p, k):
    base = 40.0
    return ((base - min(n, base)) + (base - min(p, base)) + (base - min(k, base))) / 3.0

def paravartya_ph_inversion(ph, target_ph=6.5):
    return -(ph - target_ph) * 250.0

def ekadhikena_next_stage(current_index, growth_stage):
    increments = [1.0, 1.618, 2.618, 4.236, 6.854, 11.09, 17.94, 29.03]
    return current_index + increments[min(growth_stage, 7)]

def urdhva_yield_score(soil, water, solar, temp):
    cross1 = soil * water
    cross2 = solar * temp
    vertical = soil * solar + water * temp
    return min(100.0, (cross1 + cross2 + vertical) / 30000.0 * 100.0)

def vilokanam_anomaly(values, threshold_sigma=2.0):
    if len(values) < 2: return False
    mean = sum(values) / len(values)
    var = sum((v - mean) ** 2 for v in values) / len(values)
    std = math.sqrt(var) if var > 0 else 0
    return abs(values[-1] - mean) > threshold_sigma * std if std > 0 else False

def gunakasamuccaya_wellness(ph_s, npk_s, moist_s, om_s):
    product = ph_s * npk_s * moist_s * om_s
    return min(100.0, max(0.0001, product) ** 0.25)

def shunyam_stress_balance(stress, amendment):
    residual = stress - amendment
    return 0.0 if abs(residual) < 1.0 else residual

def ahimsa_108_stress_code(nikhilam_d, paravartya_d, vilokanam_flag, wellness):
    base = (nikhilam_d / 40.0) * 60.0
    return base + abs(paravartya_d) * 2.0 + vilokanam_flag * 20.0 + (100.0 - wellness) * 0.3
