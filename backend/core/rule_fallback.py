"""Rule-based fallback when SLM is unavailable."""

def _rule_based_fallback(sensor_data, soil_type, paksha, weather, ndvi, vedic):
    ph, n, p, k, moisture, om, ec, temp = (sensor_data + [6.5, 35, 28, 40, 50, 2.0, 0.3, 28])[:8]
    
    # Soil assessment
    if ph < 5.5:
        soil_advice = "Soil is acidic. Apply lime at 2-3 tons/ha."
    elif ph > 8.0:
        soil_advice = "Soil is alkaline. Add gypsum and organic matter."
    else:
        soil_advice = "Soil pH is in good range (5.5-8.0)."
    
    # Nutrient assessment
    if n < 30:
        nutrient_advice = "Low nitrogen. Apply vermicompost (5 tons/ha) or sow green manure (dhaincha)."
    elif p < 20:
        nutrient_advice = "Low phosphorus. Add rock phosphate or bone meal."
    elif k < 25:
        nutrient_advice = "Low potassium. Apply wood ash or vermicompost."
    else:
        nutrient_advice = "NPK levels are adequate. Maintain with organic mulch."
    
    # Ahimsa directive
    if vedic.get("ahimsa_triggered"):
        ahimsa_note = "\n\n[AHIMSA-108]: Use ONLY Panchgavya (cow dung+urine+milk+curd+ghee). No chemical inputs."
    else:
        ahimsa_note = ""
    
    # Crop recommendation based on soil type and season
    crop_map = {
        "alluvial": "Rice (Sali/Boro) or Mustard",
        "laterite": "Cashew or Coconut with intercropping",
        "sandy": "Groundnut or Sweet Potato",
        "clay": "Rice or Sugarcane",
        "loamy": "Vegetables (Tomato, Brinjal, Cabbage)",
    }
    crop = crop_map.get(soil_type.lower(), "Rice or seasonal vegetables")
    
    return (
        f"SOIL REPORT ({soil_type}): {soil_advice}\n"
        f"NUTRIENTS: {nutrient_advice}\n"
        f"RECOMMENDED CROP: {crop}\n"
        f"MOON PHASE: {paksha} — {'Good for sowing' if paksha == 'waxing' else 'Good for harvesting'}"
        + ahimsa_note
    )
