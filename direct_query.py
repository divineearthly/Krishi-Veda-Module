#!/usr/bin/env python3
"""
KRISHI-VEDA DIRECT QUERY TOOL
Queries LLM directly from command line without server
"""
import subprocess, os, sys, time

LLAMA_DIR = os.path.expanduser("~/llama-b9297")

# Try models in order of preference
MODELS = [
    os.path.expanduser("~/krishi-veda-135m-f16.gguf"),
    "/storage/emulated/0/Download/krishi-veda-135m-f16.gguf",
    "/storage/emulated/0/vedic_model.gguf",
    os.path.expanduser("~/vedic_model_q2.gguf"),
    os.path.expanduser("~/qwen2.5-0.5b-instruct-q4.gguf"),
]

def find_model():
    for m in MODELS:
        if os.path.exists(m):
            return m
    return None

def query_llm(question, n_tokens=150):
    model = find_model()
    if not model:
        return "❌ No model found!"
    
    model_name = os.path.basename(model)
    size_mb = os.path.getsize(model) / (1024*1024)
    
    prompt = f"""[Krishi-Veda Agricultural AI for Indian Farmers]
Farmer's Question: {question}

Expert Agricultural Advice:"""
    
    print(f"🤖 Model: {model_name} ({size_mb:.0f}MB)")
    print(f"⏳ Generating...")
    
    start = time.time()
    
    result = subprocess.run(
        [os.path.join(LLAMA_DIR, 'llama-cli'), '-m', model,
         '-p', prompt, '-n', str(n_tokens), '--temp', '0.7', '--no-display-prompt'],
        capture_output=True, text=True,
        cwd=LLAMA_DIR,
        env={**os.environ, 'LD_LIBRARY_PATH': LLAMA_DIR},
        timeout=120
    )
    
    elapsed = time.time() - start
    
    # Clean output
    output = result.stdout
    lines = [l for l in output.split('\n') 
             if l.strip() and not any(x in l for x in ['▄', '█', 'build:', 'model:', 'modalities:', 'commands:', '/exit', 'available', 'Loading'])]
    
    clean_output = '\n'.join(lines).strip()
    
    # Extract speed
    gen_speed = "N/A"
    for line in result.stderr.split('\n') + result.stdout.split('\n'):
        if 'Generation:' in line:
            gen_speed = line.strip()
    
    print(f"⏱️  Time: {elapsed:.1f}s | {gen_speed}")
    print("-" * 50)
    print(clean_output[:1000])
    print("-" * 50)
    
    return clean_output

if __name__ == "__main__":
    print("🌾 Krishi-Veda Direct Query")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:])
    else:
        question = "What is the best organic fertilizer for rice in Assam?"
    
    print(f"📋 Question: {question}")
    print("")
    
    answer = query_llm(question, 150)
