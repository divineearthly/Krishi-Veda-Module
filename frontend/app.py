
import gradio as gr
import httpx
import asyncio
import os

# FastAPI endpoint for the running app
# This will typically be the same domain as the Gradio app on Hugging Face Spaces
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:7860")

async def call_api_v1_plan(lat, lon, soil_type, weather_desc, temperature, humidity, ndvi_value, crop_health_status, target_language):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/api/v1/plan",
                json={
                    "lat": lat,
                    "lon": lon,
                    "soil_type": soil_type,
                    "weather_desc": weather_desc,
                    "temperature": temperature,
                    "humidity": humidity,
                    "ndvi_value": ndvi_value,
                    "crop_health_status": crop_health_status,
                    "target_language": target_language
                },
                timeout=60.0 # Increased timeout for potentially long SLM inference
            )
            response.raise_for_status() # Raise an exception for HTTP errors
            result = response.json()
            return (
                result.get("vedic_plan", {}).get("final_plan", ["No plan available"]),
                result.get("vedic_plan", {}).get("vedic_insights", {}),
                result.get("slm_advice", {}).get("advice", "No SLM advice available"),
                str(result.get("external_data", {}))
            )
        except httpx.HTTPStatusError as e:
            return (f"API Error: {e.response.status_code} - {e.response.text}", "", "", "")
        except Exception as e:
            return (f"An error occurred: {e}", "", "", "")

async def call_weather_advice(lat, lon):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/weather_advice",
                json={
                    "lat": lat,
                    "lon": lon
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("weather_advice", ["No weather advice available"])
        except httpx.HTTPStatusError as e:
            return [f"API Error: {e.response.status_code} - {e.response.text}"]
        except Exception as e:
            return [f"An error occurred: {e}"]

async def call_soil_advice(lat, lon, soil_type):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/soil_advice",
                json={
                    "lat": lat,
                    "lon": lon,
                    "soil_type": soil_type
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("soil_advice", ["No soil advice available"])
        except httpx.HTTPStatusError as e:
            return [f"API Error: {e.response.status_code} - {e.response.text}"]
        except Exception as e:
            return [f"An error occurred: {e}"]

# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown(
        """
        # 🌾 Krishi-Veda Global Engine
        Sovereign offline AI for Indian agriculture — Vedic + Ahimsa

        Enter your agricultural parameters below to get personalized recommendations.
        """
    )

    with gr.Tab("Comprehensive Plan (ML + Vedic + SLM)"):
        with gr.Row():
            lat = gr.Number(label="Latitude", value=26.14)
            lon = gr.Number(label="Longitude", value=91.74)
        with gr.Row():
            soil_type = gr.Dropdown(["Alluvial", "Red", "Black", "Laterite", "Desert", "Mountain"], label="Soil Type", value="Alluvial")
            weather_desc = gr.Textbox(label="Current Weather Description (e.g., clear sky, light rain)", value="clear sky")
        with gr.Row():
            temperature = gr.Number(label="Temperature (°C)", value=19.82)
            humidity = gr.Number(label="Humidity (%)", value=85)
        with gr.Row():
            ndvi_value = gr.Number(label="NDVI Value (0.0-1.0)", value=0.414)
            crop_health_status = gr.Textbox(label="Crop Health Status (e.g., Poor, Moderate, Good)", value="Moderate")
        with gr.Row():
            target_language = gr.Dropdown(["English", "Hindi", "Assamese", "Bengali", "Telugu", "Marathi", "Tamil", "Gujarati", "Kannada", "Malayalam", "Punjabi", "Odia"], label="Target Language for SLM Advice", value="English")

        plan_btn = gr.Button("Get Comprehensive Plan")

        gr.Markdown("## Plan Output")
        final_plan_output = gr.JSON(label="Final Plan (ML + Rule-based)")
        vedic_insights_output = gr.JSON(label="Vedic Insights")
        slm_advice_output = gr.Textbox(label="SLM (AI) Advice", lines=5)
        external_data_output = gr.Textbox(label="External Data Synced", lines=3)

        plan_btn.click(
            call_api_v1_plan,
            inputs=[
                lat, lon, soil_type, weather_desc, temperature, humidity, ndvi_value, crop_health_status, target_language
            ],
            outputs=[
                final_plan_output, vedic_insights_output, slm_advice_output, external_data_output
            ]
        )

    with gr.Tab("Weather-based Advice"):
        with gr.Row():
            weather_lat = gr.Number(label="Latitude", value=26.14)
            weather_lon = gr.Number(label="Longitude", value=91.74)

        weather_btn = gr.Button("Get Weather Advice")
        weather_advice_output = gr.JSON(label="Weather Advice")

        weather_btn.click(
            call_weather_advice,
            inputs=[weather_lat, weather_lon],
            outputs=weather_advice_output
        )

    with gr.Tab("Soil-based Advice"):
        with gr.Row():
            soil_lat = gr.Number(label="Latitude", value=26.14)
            soil_lon = gr.Number(label="Longitude", value=91.74)
            soil_type_input = gr.Dropdown(["Alluvial", "Red", "Black", "Laterite", "Desert", "Mountain"], label="Soil Type", value="Alluvial")

        soil_btn = gr.Button("Get Soil Advice")
        soil_advice_output = gr.JSON(label="Soil Advice")

        soil_btn.click(
            call_soil_advice,
            inputs=[soil_lat, soil_lon, soil_type_input],
            outputs=soil_advice_output
        )

# To run the Gradio app
if __name__ == "__main__":
    # The app is designed to run on 0.0.0.0:7860 for Hugging Face Spaces compatibility
    # In a local development environment, you might run it differently or use a proxy
    # The FastAPI backend will also run on this port, Gradio will proxy requests to it.
    # In HF Spaces, the Gradio app runs on 7860, and we configure the FastAPI app to be proxied by Gradio.
    demo.launch(server_name="0.0.0.0", server_port=7860)

