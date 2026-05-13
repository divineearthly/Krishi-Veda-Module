"""
Mrid Parikshan Sutra — Vedic Soil Analysis
Classifies soil into 5 Vedic types based on NPK, pH, and moisture.
"""

class SoilAnalyzer:
    VEDIC_SOIL_TYPES = {
        "Sikta": {"pH_range": (6.0, 7.0), "texture": "Sandy", "water_holding": "Low"},
        "Panka": {"pH_range": (5.5, 6.5), "texture": "Clay", "water_holding": "High"},
        "Krishna": {"pH_range": (6.5, 7.5), "texture": "Loamy", "water_holding": "Medium"},
        "Lohita": {"pH_range": (4.5, 5.5), "texture": "Laterite", "water_holding": "Low"},
        "Pandura": {"pH_range": (7.5, 8.5), "texture": "Sandy Loam", "water_holding": "Medium"}
    }
    
    def analyze(self, soil: dict) -> dict:
        """Analyze soil and return Vedic classification."""
        N = soil.get("N", 0)
        P = soil.get("P", 0)
        K = soil.get("K", 0)
        ph = soil.get("pH", 7)
        moisture = soil.get("moisture", 50)
        
        # Classify soil type based on pH
        vedic_type = self._classify_vedic_type(ph)
        
        # Calculate health scores
        npk_score = self._npk_score(N, P, K)
        ph_score = self._ph_score(ph)
        moisture_score = self._moisture_score(moisture)
        
        overall = (npk_score + ph_score + moisture_score) / 3
        
        deficiencies = []
        if N < 30: deficiencies.append("Nitrogen")
        if P < 20: deficiencies.append("Phosphorus")
        if K < 25: deficiencies.append("Potassium")
        
        return {
            "vedic_type": vedic_type,
            "npk_score": round(npk_score, 1),
            "ph_score": round(ph_score, 1),
            "moisture_score": round(moisture_score, 1),
            "overall": round(overall, 1),
            "deficiencies": deficiencies,
            "recommendation": self._generate_recommendation(deficiencies, vedic_type)
        }
    
    def _classify_vedic_type(self, ph: float) -> str:
        for soil_type, props in self.VEDIC_SOIL_TYPES.items():
            low, high = props["pH_range"]
            if low <= ph <= high:
                return soil_type
        return "Krishna"  # default
    
    def _npk_score(self, N: float, P: float, K: float) -> float:
        scores = []
        scores.append(min(100, N * 1.5))
        scores.append(min(100, P * 2.0))
        scores.append(min(100, K * 1.8))
        return sum(scores) / 3
    
    def _ph_score(self, ph: float) -> float:
        if 6.0 <= ph <= 7.5:
            return 100
        elif 5.5 <= ph <= 8.0:
            return 70
        else:
            return 40
    
    def _moisture_score(self, moisture: float) -> float:
        if 40 <= moisture <= 70:
            return 100
        elif 20 <= moisture <= 85:
            return 70
        else:
            return 40
    
    def _generate_recommendation(self, deficiencies: list, soil_type: str) -> str:
        if not deficiencies:
            return f"Soil is healthy ({soil_type} type). Maintain current practices."
        
        rec = f"{soil_type} soil deficient in: {', '.join(deficiencies)}. "
        
        if "Nitrogen" in deficiencies:
            rec += "Apply Panchgavya (cow urine focus). "
        if "Phosphorus" in deficiencies:
            rec += "Add bone meal or rock phosphate. "
        if "Potassium" in deficiencies:
            rec += "Apply wood ash or cow dung compost. "
        
        return rec.strip()
