# Assam regional analysis - Silchar specific

ASSAM_CROP_DATA = {
    "rice": {
        "season": "kharif", "sow_month": [6, 7], "harvest_month": [11, 12],
        "water_needs": "high", "soil_ph": [5.5, 6.5],
        "organic_practices": ["vermicompost", "green_manure", "azolla"],
        "yield_ton_ha": 2.5, "varieties": ["Ranjit", "Bahadur", "Pankaj"]
    },
    "jute": {
        "season": "kharif", "sow_month": [3, 4], "harvest_month": [7, 8],
        "water_needs": "medium", "soil_ph": [6.0, 7.0],
        "organic_practices": ["compost", "neem_cake"],
        "yield_ton_ha": 2.0
    },
    "mustard": {
        "season": "rabi", "sow_month": [10, 11], "harvest_month": [2, 3],
        "water_needs": "low", "soil_ph": [6.0, 7.5],
        "organic_practices": ["mustard_cake", "wood_ash"],
        "yield_ton_ha": 1.0
    },
    "vegetables": {
        "season": "year_round", "water_needs": "medium",
        "soil_ph": [6.0, 7.0],
        "organic_practices": ["compost", "cow_dung", "mulching"],
        "common": ["brinjal", "tomato", "okra", "gourd", "spinach"]
    }
}

def get_crop_recommendation(soil_ph, season, water_available=True):
    """Recommend best crop for Silchar region based on conditions."""
    scores = {}
    for crop, data in ASSAM_CROP_DATA.items():
        score = 0
        ph_min, ph_max = data["soil_ph"]
        if ph_min <= soil_ph <= ph_max:
            score += 3
        elif abs(soil_ph - (ph_min+ph_max)/2) < 1:
            score += 1
        if data["water_needs"] == "low" or water_available:
            score += 2
        scores[crop] = score
    best = max(scores, key=scores.get)
    return {"crop": best, "details": ASSAM_CROP_DATA[best], "scores": scores}

def get_panchgavya_recipe():
    """Ahimsa-108: Panchgavya organic formulation."""
    return {
        "ingredients": "5kg cow dung + 3L cow urine + 2L milk + 2L curd + 500g ghee",
        "fermentation_days": 7,
        "application": "3olution, 300L/acre, every 15 days",
        "benefits": "Increases soil microbes, natural pest resistance, zero chemical"
    }
