import gradio as gr
from vedic_core.krishi_sutras import KrishiSutraEngine
engine = KrishiSutraEngine()
def analyze_soil(N, P, K, ph, moisture):
    result = engine.analyze({"N":N,"P":P,"K":K,"pH":ph,"moisture":moisture})
    return result.get("recommendation","Analysis pending")
demo = gr.Interface(fn=analyze_soil, inputs=[
    gr.Slider(0,100,label="N"),gr.Slider(0,100,label="P"),
    gr.Slider(0,100,label="K"),gr.Slider(0,14,label="pH"),
    gr.Slider(0,100,label="Moisture %")],
    outputs="text",title="🌾 Krishi-Veda",description="Vedic agricultural intelligence")
demo.launch()
