
import os
import numpy as np
import tensorflow as tf
import onnx
from onnxruntime.quantization import quantize_static, QuantType, CalibrationDataReader

def check_file_size(file_path, limit_mb=10):
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb <= limit_mb:
        print(f'✅ {os.path.basename(file_path)} size: {size_mb:.2f} MB (Within limit)')
    else:
        print(f'❌ {os.path.basename(file_path)} size: {size_mb:.2f} MB (Exceeds {limit_mb}MB!)')

# 1. TFLite INT8 Quantization
def convert_to_tflite_int8(keras_model, output_path, representative_data):
    print('--- Starting TFLite INT8 Quantization ---')
    converter = tf.lite.TFLiteConverter.from_keras_model(keras_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    def representative_dataset_gen():
        for val in representative_data:
            yield [val.astype(np.float32)]
            
    converter.representative_dataset = representative_dataset_gen
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    
    tflite_model = converter.convert()
    with open(output_path, 'wb') as f:
        f.write(tflite_model)
    check_file_size(output_path)

# 2. ONNX INT8 Quantization (Conceptual Skeleton)
class SimpleCalibrationDataReader(CalibrationDataReader):
    def __init__(self, data_list, input_name):
        self.data = iter([{input_name: d} for d in data_list])
    def get_next(self):
        return next(self.data, None)

def quantize_onnx_model(model_fp32_path, output_quant_path, representative_data, input_name):
    print('--- Starting ONNX INT8 Quantization ---')
    dr = SimpleCalibrationDataReader(representative_data, input_name)
    quantize_static(
        model_fp32_path,
        output_quant_path,
        dr,
        quant_format=QuantType.QInt8
    )
    check_file_size(output_quant_path)

if __name__ == '__main__':
    # Example Dummy Model and Data for validation
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(8,)),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    dummy_data = [np.random.rand(1, 8) for _ in range(50)]
    
    out_dir = 'Krishi-Veda-Module_v2/ai_models/quantized/'
    os.makedirs(out_dir, exist_ok=True)
    
    # Convert TFLite
    convert_to_tflite_int8(model, os.path.join(out_dir, 'soil_model.tflite'), dummy_data)
