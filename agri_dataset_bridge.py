import ctypes
import numpy as np
import os
import platform

def load_cpp_kernel(kernel_name):
    """Loads a C++ shared library kernel based on the current architecture."""
    arch = platform.machine().lower()
    
    # Deployment target (ARM64)
    arm_path = f"Divine-Earthly-Quantum-Vedic-Kernels/build/arm64/{kernel_name}.so"
    # Local development/test target (x86_64)
    src_path = f"Divine-Earthly-Quantum-Vedic-Kernels/src/{kernel_name}.so"

    # If we are on ARM (IoT device), prioritize ARM build
    if "arm" in arch or "aarch64" in arch:
        target_path = arm_path if os.path.exists(arm_path) else src_path
    else:
        # On Colab (x86_64), use the local compiled source
        target_path = src_path

    try:
        return ctypes.CDLL(target_path)
    except OSError as e:
        print(f"Error loading {kernel_name} from {target_path}: {e}")
        return None

def apply_ahimsa_protocol(nutrient_recommendations, harmony_threshold=100.0):
    """Applies the Ahimsa Protocol to cap nutrient recommendations."""
    print(f"Applying Ahimsa Protocol with Harmony Threshold: {harmony_threshold}...")
    return np.minimum(nutrient_recommendations, harmony_threshold)

def agri_data_pipeline(soil_moisture_data, weather_api_data, current_nutrients=None):
    """Simulates feeding agri-data into C++ kernels."""
    print(f"-- Agri-Data Pipeline Started (Host Arch: {platform.machine()}) --")

    # 1. Anurupyena (Scaling)
    input_moisture = np.array(soil_moisture_data, dtype=np.float32)
    output_moisture = np.zeros_like(input_moisture)
    anurupyena_kernel = load_cpp_kernel("anurupyena_sutra")
    if anurupyena_kernel:
        anurupyena_kernel.anurupyena_scale.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_float, ctypes.POINTER(ctypes.c_float)]
        anurupyena_kernel.anurupyena_scale(input_moisture.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), len(input_moisture), 0.8, output_moisture.ctypes.data_as(ctypes.POINTER(ctypes.c_float)))
        print("Anurupyena Scaled Moisture:", output_moisture)

    # 2. Paravartya (Routing/Optimization)
    input_weather = np.array(weather_api_data, dtype=np.int32)
    output_logistics = np.zeros_like(input_weather)
    paravartya_kernel = load_cpp_kernel("paravartya_sutra")
    if paravartya_kernel:
        paravartya_kernel.paravartya_optimize.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        paravartya_kernel.paravartya_optimize(input_weather.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), len(input_weather), 0, output_logistics.ctypes.data_as(ctypes.POINTER(ctypes.c_int)))
        print("Paravartya Optimized Logistics:", output_logistics)

    # 3. Nikhilam (Nutrient Balancing)
    output_deficits = None
    if current_nutrients is not None:
        input_nutrients = np.array(current_nutrients, dtype=np.int32)
        output_deficits = np.zeros_like(input_nutrients)
        nikhilam_kernel = load_cpp_kernel("nikhilam_sutra")
        if nikhilam_kernel:
            nikhilam_kernel.calculate_nutrient_deficit.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
            nikhilam_kernel.calculate_nutrient_deficit(input_nutrients.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), len(input_nutrients), output_deficits.ctypes.data_as(ctypes.POINTER(ctypes.c_int)))
            print("Nikhilam Calculated Deficits (NPK):", output_deficits)

    print("-- Agri-Data Pipeline Finished --")
    return output_moisture, output_logistics, output_deficits

if __name__ == '__main__':
    agri_data_pipeline([10.5, 12.0], [25, 30], current_nutrients=[70, 85, 90])
