
import ctypes
import os

# Load the shared library
try:
    _vedic_kernels = ctypes.CDLL(os.path.abspath("Krishi-Veda-Module/vedic_engine/vedic_kernels.so"))
except OSError as e:
    raise RuntimeError(f"Could not load vedic_kernels.so: {e}")

# Define function signatures for Anurupyena metric
# int calculate_anurupyena_metric(int a, int b);
_vedic_kernels.calculate_anurupyena_metric.argtypes = [ctypes.c_int, ctypes.c_int]
_vedic_kernels.calculate_anurupyena_metric.restype = ctypes.c_int

def calculate_anurupyena_metric(a: int, b: int) -> int:
    """Calculates the Anurupyena metric using the C++ kernel."""
    return _vedic_kernels.calculate_anurupyena_metric(a, b)

# Define function signatures for Paravartya index
# double get_paravartya_index(double val);
_vedic_kernels.get_paravartya_index.argtypes = [ctypes.c_double]
_vedic_kernels.get_paravartya_index.restype = ctypes.c_double

def get_paravartya_index(val: float) -> float:
    """Gets the Paravartya index using the C++ kernel."""
    return _vedic_kernels.get_paravartya_index(val)

# Define function signatures for Ahimsa Governance message
# void print_ahimsa_governance_message();
_vedic_kernels.print_ahimsa_governance_message.argtypes = []
_vedic_kernels.print_ahimsa_governance_message.restype = None

def print_ahimsa_governance_message():
    """Prints the Ahimsa Governance message from the C++ kernel."""
    _vedic_kernels.print_ahimsa_governance_message()


if __name__ == '__main__':
    print("--- Testing vedic_bridge.py ---")

    # Test Anurupyena metric
    anurupyena_result = calculate_anurupyena_metric(5, 7)
    print(f"Anurupyena Metric for (5, 7): {anurupyena_result}")

    # Test Paravartya index
    paravartya_result = get_paravartya_index(100.0)
    print(f"Paravartya Index for (100.0): {paravartya_result}")

    # Test Ahimsa Governance message
    print("Ahimsa Governance Message:")
    print_ahimsa_governance_message()

    print("--- vedic_bridge.py tests complete ---")
