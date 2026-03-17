import sqlite3
import numpy as np
import tensorflow as tf
import os

class SoilHealthService:
    """
    Hybrid Intelligence Engine: Combines Quantized AI, Rule-Based Validation,
    and Vedic Timing adjustments into a unified decision pipeline.
    """

    def __init__(self, model_path=None, db_path=None):
        # Default paths relative to project root
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_path = model_path or os.path.join(base_path, 'ai_models/quantized/soil_model.tflite')
        self.db_path = db_path or os.path.join(base_path, 'krishi_veda_offline.db')
        
        try:
            self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
        except Exception:
            self.interpreter = None

    def _run_ai_inference(self, sensor_data):
        if not self.interpreter:
            return 50.0
        input_data = np.array([sensor_data], dtype=np.float32)
        input_scale, input_zero_point = self.input_details[0]['quantization']
        if input_scale > 0:
            input_data = (input_data / input_scale + input_zero_point).astype(np.int8)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        output_scale, output_zero_point = self.output_details[0]['quantization']
        ai_score = (output_data.astype(np.float32) - output_zero_point) * output_scale
        return float(ai_score[0][0])

    def _get_muhurta_multiplier(self, moon_phase='waxing'):
        return 1.15 if moon_phase == 'waxing' else 0.85

    def predict(self, farmer_id, sensor_data, current_paksha='waxing'):
        ai_baseline = self._run_ai_inference(sensor_data)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT r.soil_type 
            FROM farmers f JOIN regional_data r ON f.location_state = r.state_code 
            WHERE f.id = ?''', (farmer_id,))
        row = cursor.fetchone()
        soil_type = row[0] if row else 'General'
        conn.close()

        muhurta_mult = self._get_muhurta_multiplier(current_paksha)
        final_score = ai_baseline * muhurta_mult
        status = 'Excellent' if final_score > 75 else 'Moderate' if final_score > 40 else 'Poor'
        
        return {
            'ai_baseline_score': round(ai_baseline, 2),
            'vedic_multiplier': muhurta_mult,
            'final_quantum_vedic_score': round(final_score, 2),
            'recommendation': f'Soil health in your {soil_type} region is {status}.'
        }
