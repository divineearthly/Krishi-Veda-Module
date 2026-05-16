
# Assam Silchar Regional Crop Database
ASSAM_CROP_DATA = {
    "rice": {
        "season": "kharif", "sow_month": [6, 7], "harvest_month": [11, 12],
        "water_needs": "high", "soil_ph": [5.5, 6.5],
        "organic_practices": ["vermicompost", "green_manure", "azolla"],
        "yield_ton_ha": 2.5,
        "varieties": ["Ranjit", "Bahadur", "Pankaj", "Shahbhagi"],
        "market_rate_kg": 22
    },
    "jute": {
        "season": "kharif", "sow_month": [3, 4], "harvest_month": [7, 8],
        "water_needs": "medium", "soil_ph": [6.0, 7.0],
        "organic_practices": ["compost", "neem_cake"],
        "yield_ton_ha": 2.0,
        "varieties": ["JRO-524", "JRO-8432"],
        "market_rate_kg": 45
    },
    "mustard": {
        "season": "rabi", "sow_month": [10, 11], "harvest_month": [2, 3],
        "water_needs": "low", "soil_ph": [6.0, 7.5],
        "organic_practices": ["mustard_cake", "wood_ash", "panchgavya"],
        "yield_ton_ha": 1.0,
        "varieties": ["TS-46", "Varuna", "Pusa Bold"],
        "market_rate_kg": 55
    },
    "vegetables": {
        "season": "year_round", "water_needs": "medium",
        "soil_ph": [6.0, 7.0],
        "organic_practices": ["compost", "cow_dung", "mulching"],
        "common": ["brinjal", "tomato", "okra", "gourd", "spinach", "cauliflower"],
        "market_rate_kg": 30
    },
    "tea": {
        "season": "perennial", "sow_month": [5, 6], "harvest_month": [3, 11],
        "water_needs": "high", "soil_ph": [4.5, 5.5],
        "organic_practices": ["compost", "mulching", "cow_dung"],
        "yield_ton_ha": 1.5,
        "varieties": ["TV1", "TV23", "S3A3"],
        "market_rate_kg": 200
    },
    "bamboo": {
        "season": "year_round", "water_needs": "medium",
        "soil_ph": [5.5, 7.0],
        "organic_practices": ["compost", "mulching"],
        "varieties": ["Bambusa balcooa", "Bambusa tulda"],
        "market_rate_pole": 150
    }
}

PANCHGAVYA_RECIPE = {
    "ingredients": {
        "cow_dung_kg": 5,
        "cow_urine_L": 3,
        "cow_milk_L": 2,
        "curd_L": 2,
        "ghee_g": 500
    },
    "fermentation_days": 7,
    "application": "3% solution, 300L/acre, every 15 days",
    "benefits": [
        "Increases soil microbes 100x",
        "Natural pest resistance",
        "Improves soil structure",
        "Zero chemical residue"
    ]
}

SILCHAR_SOIL_TYPES = {
    "alluvial": {"ph": 6.0, "texture": "sandy_loam", "area_pct": 35},
    "lateritic": {"ph": 5.5, "texture": "loamy", "area_pct": 25},
    "clay": {"ph": 6.5, "texture": "clay_loam", "area_pct": 20},
    "sandy": {"ph": 5.8, "texture": "sandy", "area_pct": 20}
}
