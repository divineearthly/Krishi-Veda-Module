"""
Krishi-Veda Gradio UI — Offline Agricultural Assistant
Uses actual PlanRequest fields: sensor_data, soil_type, paksha, use_slm
"""
import gradio as gr
import httpx
import json

API_BASE = "http://localhost:7860"

async def call_api_v1_plan(sensor_ph, sensor_n, sensor_p, sensor_k, soil_type, paksha, use_slm):
    """Call the /api/v1/plan endpoint with correct field names."""
    payload = {
        "sensor_data": [float(sensor_ph), float(sensor_n), float(sensor_p), float(sensor_k)],
        "soil_type": soil_type,
        "paksha": paksha,
        "use_slm": use_slm,
    }
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{API_BASE}/api/v1/plan", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return json.dumps(data, indent=2, ensure_ascii=False)
            return f"Error {resp.status_code}: {resp.text}"
    except Exception as e:
        return f"Connection error: {e}"

# ── Gradio Interface ────────────────────────────────────────────────────────
def create_ui():
    with gr.Blocks(title="Krishi-Veda | कृषि-वेद", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Krishi-Veda | कृषि-वेद\n### Vedic Agricultural AI Assistant")
        
        with gr.Row():
            with gr.Column(scale=1):
                soil_type = gr.Dropdown(
                    ["Alluvial", "Black", "Red", "Laterite", "Sandy", "Clay", "Loamy", "General"],
                    label="Soil Type", value="General"
                )
                paksha = gr.Radio(
                    ["waxing", "waning"],
                    label="Moon Phase (Paksha)", value="waxing"
                )
                use_slm = gr.Checkbox(label="Use SLM (AI Model)", value=True)
                
            with gr.Column(scale=2):
                with gr.Row():
                    sensor_ph = gr.Slider(0, 14, value=6.5, step=0.1, label="Soil pH")
                    sensor_n = gr.Slider(0, 100, value=35, step=1, label="Nitrogen (N) ppm")
                with gr.Row():
                    sensor_p = gr.Slider(0, 100, value=28, step=1, label="Phosphorus (P) ppm")
                    sensor_k = gr.Slider(0, 100, value=40, step=1, label="Potassium (K) ppm")
        
        submit_btn = gr.Button("🌾 Get Farming Plan", variant="primary")
        output = gr.Textbox(label="Krishi-Veda Advice", lines=20, max_lines=30)
        
        submit_btn.click(
            fn=call_api_v1_plan,
            inputs=[sensor_ph, sensor_n, sensor_p, sensor_k, soil_type, paksha, use_slm],
            outputs=output
        )
    
    return demo

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(server_name="0.0.0.0", server_port=7861)
