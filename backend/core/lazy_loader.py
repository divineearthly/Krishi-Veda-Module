import importlib
import os
import time

class LazyServiceLoader:
    """Manages lazy instantiation and hot-swapping of heavy backend services."""
    def __init__(self):
        self._soil_service = None
        self._last_model_timestamp = 0
        # Resolve paths relative to the project root
        self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_dir = os.path.join(self.base_path, 'ai_models', 'quantized')
        self.model_path = os.path.join(self.model_dir, 'soil_model.tflite')

    def _check_for_model_update(self):
        """Checks if a newer model exists on disk based on modification time."""
        if not os.path.exists(self.model_path):
            return False
        
        current_mtime = os.path.getmtime(self.model_path)
        if current_mtime > self._last_model_timestamp:
            print(f'--- New model version detected (mtime: {current_mtime}) ---')
            return True
        return False

    @property
    def soil_service(self):
        """Returns the SoilHealthService instance, hot-swapping if a new model is found."""
        is_update_available = self._check_for_model_update()
        
        if self._soil_service is None or is_update_available:
            try:
                print('--- Loading/Hot-swapping SoilHealthService ---')
                module = importlib.import_module('backend.services.soil_health')
                # Force re-instantiation to load the new model file
                new_service = module.SoilHealthService()
                
                # Update state only if load succeeds
                self._soil_service = new_service
                self._last_model_timestamp = os.path.getmtime(self.model_path) if os.path.exists(self.model_path) else 0
            except Exception as e:
                print(f'--- Error during hot-swap: {e}. Falling back to previous stable version. ---')
                if self._soil_service is None:
                    raise e # Critical failure on first load
        
        return self._soil_service

# Global loader instance
loader = LazyServiceLoader()