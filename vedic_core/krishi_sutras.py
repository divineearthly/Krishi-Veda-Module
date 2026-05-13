"""
8 Krishi-Sutras mapped to computational agriculture.
Based on Vedic principles for sustainable farming.
"""

SUTRAS = {
    1: {
        "name": "Ahimsa-108 Protocol",
        "sanskrit": "अहिंसा परमो धर्मः",
        "meaning": "Non-violence is the highest duty",
        "application": "Chemical-free farming, natural pest control",
        "threshold": 108  # sacred number for soil health scoring
    },
    2: {
        "name": "Panchgavya Sutra",
        "sanskrit": "पञ्चगव्य",
        "meaning": "Five cow products",
        "application": "Organic fertilizer: milk, curd, ghee, dung, urine",
        "npk_ratio": {"N": 1.2, "P": 0.8, "K": 0.5}
    },
    3: {
        "name": "Ritu Chakra Sutra",
        "sanskrit": "ऋतु चक्र",
        "meaning": "Seasonal cycle",
        "application": "Crop rotation based on Vedic calendar",
        "seasons": ["Vasant", "Grishma", "Varsha", "Sharad", "Hemant", "Shishir"]
    },
    4: {
        "name": "Jal Samrakshan Sutra",
        "sanskrit": "जल संरक्षण",
        "meaning": "Water conservation",
        "application": "Vedic irrigation timing and moisture management"
    },
    5: {
        "name": "Mrid Parikshan Sutra",
        "sanskrit": "मृद परीक्षण",
        "meaning": "Soil examination",
        "application": "Vedic soil classification system",
        "soil_types": ["Sikta", "Panka", "Krishna", "Lohita", "Pandura"]
    },
    6: {
        "name": "Bija Samskara Sutra",
        "sanskrit": "बीज संस्कार",
        "meaning": "Seed treatment",
        "application": "Natural seed purification before sowing"
    },
    7: {
        "name": "Sah-Fasal Sutra",
        "sanskrit": "सह फसल",
        "meaning": "Companion cropping",
        "application": "Multi-crop synergy based on Vedic plant affinities"
    },
    8: {
        "name": "Kosha Sutra",
        "sanskrit": "कोश",
        "meaning": "Treasury/Store",
        "application": "Grain storage using Vedic preservation methods"
    }
}

class KrishiSutraEngine:
    """Core engine applying 8 Krishi-Sutras to agricultural data."""
    
    def __init__(self):
        self.sutras = SUTRAS
        self.soil_analyzer = None
        self.crop_recommender = None
    
    def analyze(self, soil_data: dict) -> dict:
        """
        Analyze soil using Vedic principles.
        
        Args:
            soil_data: {"N": float, "P": float, "K": float, "pH": float, "moisture": float}
        
        Returns:
            dict with recommendations
        """
        from .soil_analysis import SoilAnalyzer
        from .crop_recommendation import CropRecommender
        
        if self.soil_analyzer is None:
            self.soil_analyzer = SoilAnalyzer()
        if self.crop_recommender is None:
            self.crop_recommender = CropRecommender()
        
        # Apply Sutra 5: Mrid Parikshan (Soil Examination)
        soil_health = self.soil_analyzer.analyze(soil_data)
        
        # Apply Sutra 1: Ahimsa-108 scoring
        ahimsa_score = self._calculate_ahimsa_score(soil_health)
        
        # Apply Sutra 3: Ritu Chakra (Seasonal recommendation)
        import datetime
        season = self._get_current_season(datetime.datetime.now().month)
        
        # Apply Sutra 2: Panchgavya recommendation
        panchgavya = self._recommend_panchgavya(soil_data)
        
        # Crop recommendation
        crops = self.crop_recommender.recommend(soil_data, season)
        
        return {
            "soil_health": soil_health,
            "ahimsa_score": ahimsa_score,
            "current_season": season,
            "panchgavya_recommendation": panchgavya,
            "recommended_crops": crops[:5],
            "sutras_applied": ["1", "2", "3", "5", "7"]
        }
    
    def _calculate_ahimsa_score(self, soil_health: dict) -> float:
        """Score soil health on the sacred 108 scale."""
        base = soil_health.get("overall", 50)
        return min(108, base * 1.08)
    
    def _get_current_season(self, month: int) -> str:
        seasons = {
            1: "Shishir", 2: "Shishir",
            3: "Vasant", 4: "Vasant",
            5: "Grishma", 6: "Grishma",
            7: "Varsha", 8: "Varsha",
            9: "Sharad", 10: "Sharad",
            11: "Hemant", 12: "Hemant"
        }
        return seasons.get(month, "Vasant")
    
    def _recommend_panchgavya(self, soil: dict) -> str:
        """Recommend Panchgavya application based on NPK deficiency."""
        n_def = soil.get("N", 50) < 40
        p_def = soil.get("P", 50) < 40
        k_def = soil.get("K", 50) < 40
        
        if any([n_def, p_def, k_def]):
            ratio = "1:2:3"  # Milk:Urine:Dung
            freq = "Weekly" if sum([n_def, p_def, k_def]) >= 2 else "Bi-weekly"
            return f"Apply Panchgavya ({ratio}) — {freq}"
        return "Soil NPK adequate. Panchgavya not required."
