"""
Krishi-Veda Global Engine — Hugging Face Space entry point.
"""
import streamlit as st

st.set_page_config(page_title="Krishi-Veda", layout="centered")
st.title("🌾 Krishi-Veda Global Engine")
st.caption("Vedic Agricultural Intelligence — Serving All Living Beings")

st.markdown("""
### 🕉️ Krishi-Veda API

FastAPI backend with 8 Vedic Sutras, Ahimsa-108 Protocol, 135M SLM, NASA POWER weather.

| Endpoint | Description |
|----------|-------------|
| `/health` | System health |
| `/api/v1/plan` | Full Vedic farm plan |
| `/api/v1/slm/advice` | AI farming advice |

[GitHub](https://github.com/divineearthly/Krishi-Veda-Module)
""")
