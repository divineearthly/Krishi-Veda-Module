import os
import subprocess

# Safely handle the custom Vedic kernel import for Hugging Face
try:
    import vedic_inference_engine
    HAS_VEDIC_ENGINE = True
except ImportError:
    HAS_VEDIC_ENGINE = False
    print("Warning: vedic_inference_engine not found. Running in cloud/fallback mode.")

# Local Termux paths
LLAMA_CLI_PATH = os.path.expanduser("~/llama-b9297/llama-cli")
MODEL_PATH = "/root/vedic-krishi-135m-q4.gguf"

def _infer(prompt):
    """
    Executes Llama inference if running locally on Termux.
    Fails gracefully to a string if deployed on Hugging Face.
    """
    if not os.path.exists(LLAMA_CLI_PATH) or not os.path.exists(MODEL_PATH):
        return "" # Returns empty string so app.py falls back to pure Python rule-based advice
    
    try:
        # Execute the local SLM via llama.cpp
        result = subprocess.run(
            [LLAMA_CLI_PATH, "-m", MODEL_PATH, "-p", prompt, "-n", "128", "--temp", "0.2"],
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Inference error: {e}")
        return ""
