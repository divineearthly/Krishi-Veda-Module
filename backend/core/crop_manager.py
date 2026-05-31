import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, "data", "crop_registry.json")

class CropManager:
    def __init__(self):
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"regions": {}, "climate_zones": {}}

    def get_crops_for_region(self, region_name, season="kharif"):
        region_key = region_name.strip().lower()
        if "regions" in self.data and region_key in self.data["regions"]:
            crops = self.data["regions"][region_key]["crops"].get(season.lower(), [])
            if crops:
                return f"Recommended for {region_name.title()} ({season}): {', '.join(crops)}."
        return (f"Region '{region_name}' not found. "
                f"General tropical recommendations: Cassava, Sugarcane, Rice, Banana.")

crop_manager = CropManager()
