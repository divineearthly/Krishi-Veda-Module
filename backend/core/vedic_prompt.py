"""
Production Vedic Prompts — Force specific, actionable answers.
Designed for 0.5B models with 256-512 token context.
"""

def build_farming_prompt(grounding_text, soil_type, temp, rain, ndvi_val,
                         ahimsa_triggered=False, language="en"):
    """
    Multiple-choice style prompt that forces the model to pick specific options
    rather than explaining general principles.
    """
    
    # Crop recommendations by soil type
    crop_options = {
        "alluvial": "Rice (Sali variety) or Mustard",
        "laterite": "Cashew with pepper intercropping or Coconut",
        "sandy": "Groundnut or Sweet Potato",
        "clay": "Rice or Sugarcane",
        "loamy": "Tomato, Brinjal, or Cabbage",
    }
    crops = crop_options.get(soil_type.lower(), "Rice or seasonal vegetables")
    
    # Fertilizer based on Ahimsa
    if ahimsa_triggered:
        fertilizer = "Panchgavya (5kg cow dung + 5L cow urine + 2L milk + 2L curd + 1kg ghee, fermented 15 days)"
        fertilizer_short = "Panchgavya organic mix ONLY"
    else:
        fertilizer = "Vermicompost 5 tons/ha OR Panchgavya organic mix"
        fertilizer_short = "Vermicompost or Panchgavya"
    
    # Water guidance
    if "rice" in crops.lower():
        water = "Maintain 5cm standing water. Irrigate every 7-10 days if no rain."
    else:
        water = "Irrigate every 5-7 days. Drip irrigation recommended."
    
    # Timing based on temperature
    if temp > 30:
        timing = "Plant in early morning or evening. Provide shade for seedlings."
    elif temp < 20:
        timing = "Wait for temperature to rise above 20°C. Prepare nursery now."
    else:
        timing = "Plant now. Conditions are favorable."
    
    prompt = f"""You are a farmer in Assam giving advice to your neighbor.

FIELD DATA:
- Soil: {soil_type} ({grounding_text})
- Temperature: {temp}°C, Rain: {rain}mm/month, NDVI: {ndvi_val}

INSTRUCTIONS: Answer these 4 questions. One line each. No explanations.

1. CROP TO PLANT: [{crops}] → Pick the best one for this soil.
2. FERTILIZER: [{fertilizer_short}] → Say exactly how much.
3. WHEN TO PLANT: [{timing}]
4. WATER: [{water}]

Your advice (4 lines only):"""
    
    return prompt


def build_farmer_chat_prompt(farmer_question, soil_context, ahimsa_triggered=False):
    """
    For free-form farmer questions. Keeps answers short and practical.
    """
    ahimsa_note = " CRITICAL: You must ONLY recommend organic/Panchgavya methods. Never suggest chemicals." if ahimsa_triggered else ""
    
    return f"""You are an experienced farmer from Assam. Give short, practical advice.
{soil_context}{ahimsa_note}

Farmer asks: {farmer_question}

Your answer (2-3 sentences, simple words):"""


# Keep the original Panchakosha for documentation/research
def build_panchakosha_prompt(grounding_text, soil_type, temp, rain, ndvi_val,
                              language="en", ahimsa_triggered=False):
    """
    Full Panchakosha reasoning prompt — for research/demo use.
    Requires larger context window (512+ tokens).
    """
    lang = {"en": "Respond in simple English.", 
            "as": "অসমীয়াত উত্তৰ দিয়ক।",
            "hi": "हिंदी में उत्तर दें।",
            "bn": "বাংলায় উত্তর দিন।"}.get(language, "Respond in simple English.")
    
    ahimsa_directive = ("[AHIMSA-108 ACTIVE] Recommend ONLY Panchgavya organic methods."
                        if ahimsa_triggered else "Prefer organic methods where possible.")
    
    return (
        f"You are a Vedic agricultural advisor following Panchakosha wisdom.\n\n"
        f"ANNAMAYA (Physical): {soil_type} soil, {temp}°C, {rain}mm rain, NDVI {ndvi_val}\n"
        f"PRANAMAYA (Energy): {grounding_text}\n"
        f"MANOMAYA (Wisdom): Recall traditional Assamese farming knowledge.\n"
        f"VIJNANAMAYA (Ethics): {ahimsa_directive}\n"
        f"ANANDAMAYA (Action): Give practical advice the farmer can use today.\n\n"
        f"{lang}\n\nGive a 5-line farming plan (crop, fertilizer, timing, water, pest control):"
    )


def build_simple_prompt(grounding_text, soil_type, temp, rain, ndvi_val, ahimsa_triggered):
    """Simplest possible prompt for Q2 models."""
    ahimsa = "Use Panchgavya organic ONLY." if ahimsa_triggered else "Use organic where possible."
    return (
        f"Assam farmer advisor.\n"
        f"Soil: {soil_type}. {grounding_text}. {temp}°C, {rain}mm rain.\n"
        f"{ahimsa}\n"
        f"Give a 3-line farming plan (crop, fertilizer, timing):"
    )
