"""
Sah-Fasal Sutra + Ritu Chakra — Vedic crop recommendation.
"""

class CropRecommender:
    SEASONAL_CROPS = {
        "Vasant": ["Wheat", "Barley", "Mustard", "Chickpea", "Peas"],
        "Grishma": ["Watermelon", "Cucumber", "Pumpkin", "Bitter Gourd", "Okra"],
        "Varsha": ["Rice", "Maize", "Sugarcane", "Cotton", "Jute"],
        "Sharad": ["Millet", "Sorghum", "Groundnut", "Soybean", "Sunflower"],
        "Hemant": ["Wheat", "Gram", "Lentil", "Flax", "Safflower"],
        "Shishir": ["Barley", "Oats", "Mustard", "Linseed", "Fenugreek"]
    }
    
    COMPANION_PLANTS = {
        "Rice": ["Azolla", "Duckweed"],
        "Wheat": ["Chickpea", "Mustard"],
        "Maize": ["Beans", "Pumpkin"],
        "Cotton": ["Onion", "Garlic"],
        "Sugarcane": ["Coriander", "Fenugreek"]
    }
    
    def recommend(self, soil: dict, season: str) -> list:
        """Recommend crops based on soil conditions and season."""
        ph = soil.get("pH", 7)
        moisture = soil.get("moisture", 50)
        
        candidates = self.SEASONAL_CROPS.get(season, self.SEASONAL_CROPS["Vasant"])
        
        scored = []
        for crop in candidates:
            score = self._crop_soil_match(crop, ph, moisture)
            scored.append((crop, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        recommendations = []
        for crop, score in scored:
            companions = self.COMPANION_PLANTS.get(crop, [])
            recommendations.append({
                "crop": crop,
                "suitability": score,
                "companion_plants": companions
            })
        
        return recommendations
    
    def _crop_soil_match(self, crop: str, ph: float, moisture: float) -> int:
        """Score crop suitability based on soil conditions."""
        score = 100
        
        # pH suitability (simplified)
        optimal_ph = {"Rice": 5.5, "Wheat": 6.5, "Maize": 6.0, "Sugarcane": 6.5}
        crop_ph = optimal_ph.get(crop, 6.5)
        ph_diff = abs(ph - crop_ph)
        score -= ph_diff * 10
        
        # Moisture penalty
        if moisture < 30 or moisture > 80:
            score -= 20
        
        return max(0, min(100, int(score)))
