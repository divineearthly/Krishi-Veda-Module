import json
import random
import sys
import os

# Import the Google Cloud Translation client library
from google.cloud import translate

# Ensure vedic_bridge is in path and imported if not already
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import vedic_bridge

def ahimsa_harmony_index() -> float:
    """Calculates a dummy Ahimsa Harmony Index using C++ kernel functions."""
    metric_anurupyena = vedic_bridge.calculate_anurupyena_metric(random.randint(50, 150), random.randint(1, 10))
    index_paravartya = vedic_bridge.get_paravartya_index(random.uniform(50.0, 200.0))
    return metric_anurupyena + index_paravartya

def generate_farmer_advice(soil_data: dict, weather_data: dict, language_code: str = 'en') -> str:
    """
    Generates farmer advice, including Vedic override and multilingual translation.

    Args:
        soil_data (dict): Dictionary containing soil information.
        weather_data (dict): Dictionary containing weather information.
<<<<<<< HEAD
        language_code (str): Target language code (e.g., 'en', 'bn', 'hi').
=======
        language_code (str): Target language code (e.e.g., 'en', 'bn', 'hi').
>>>>>>> 750b2b3 (Re-initialized, recreated all files, and committed latest Krishi-Veda FastAPI project files.)

    Returns:
        str: JSON string with translated farmer advice.
    """
    # Instantiates a client for Google Cloud Translation
    translate_client = translate.TranslationServiceClient()

    # Get project_id from environment variable, which will be set by Cloud Run
    project_id = os.environ.get('PROJECT_ID')
    if not project_id:
<<<<<<< HEAD
        raise RuntimeError("PROJECT_ID environment variable not set. This is required for Google Cloud Translation API.")
=======
        # For local testing, use a dummy project ID or handle it gracefully
        # In a deployed environment, this env var will be set.
        # raise RuntimeError("PROJECT_ID environment variable not set. This is required for Google Cloud Translation API.")
        print("Warning: PROJECT_ID environment variable not set. Using a placeholder for translation API.")
        project_id = "your-gcp-project-id" # Placeholder for local testing

>>>>>>> 750b2b3 (Re-initialized, recreated all files, and committed latest Krishi-Veda FastAPI project files.)
    # Correctly construct the parent string
    parent = f"projects/{project_id}/locations/global"


    harmony_index = ahimsa_harmony_index()
    # print(f"\nAhimsa Harmony Index calculated: {harmony_index:.2f}") # Comment out for cleaner server logs

    crop_recommendation = "Rice"
    weather_risk = "Low risk of pests due to moderate humidity."
    irrigation_advice = "Water twice a day, morning and evening."

    if harmony_index > 108:
        # print("\n--- VEDIC OVERRIDE ACTIVATED! ---") # Comment out for cleaner server logs
        # vedic_bridge.print_ahimsa_governance_message() # Comment out for cleaner server logs
        crop_recommendation = "Organic millet, suitable for drought conditions."
        weather_risk = "High risk, consider natural pest control methods and traditional drought-resistant crops."
        irrigation_advice = "Utilize rainwater harvesting and efficient drip irrigation with natural microbial enhancers."
        override_message = "Vedic principles recommend sustainable, organic alternatives due to high Ahimsa disharmony."
    else:
        override_message = "Standard recommendations apply."

    if soil_data.get('pH') < 6.0:
        crop_recommendation += " (consider liming)"
    if weather_data.get('temperature') > 35:
        irrigation_advice += " Increase water frequency during peak heat."

    advice = {
        "ahimsa_harmony_index": round(harmony_index, 2),
        "override_status": override_message,
        "crop_recommendation": crop_recommendation,
        "weather_risk": weather_risk,
        "irrigation_advice": irrigation_advice,
        "soil_info": soil_data,
        "weather_info": weather_data
    }

    translated_advice = {}
    for key, value in advice.items():
        if isinstance(value, str) and key not in ['override_status']:
            try:
                response = translate_client.translate_text(
                    request={
                        "parent": parent,
                        "contents": [value],
                        "target_language_code": language_code
                    }
                )
                translated_advice[key] = response.translations[0].translated_text
            except Exception as e:
                # print(f"Warning: Could not translate '{value}' to {language_code}. Error: {e}") # Comment out for cleaner server logs
                translated_advice[key] = value
        elif isinstance(value, dict):
            translated_advice[key] = value
        else:
            translated_advice[key] = value

    # Translate the override message separately as it's generated dynamically
    try:
        if language_code != 'en':
            response = translate_client.translate_text(
                request={
                    "parent": parent,
                    "contents": [override_message],
                    "target_language_code": language_code
                }
            )
            translated_advice['override_status'] = response.translations[0].translated_text
        else:
            translated_advice['override_status'] = override_message
    except Exception as e:
        # print(f"Warning: Could not translate override message. Error: {e}")
        translated_advice['override_status'] = override_message

    return json.dumps(translated_advice, indent=4, ensure_ascii=False)
