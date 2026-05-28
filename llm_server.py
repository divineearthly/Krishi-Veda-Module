"""
Krishi-Veda LLM Server — serves GGUF model via HTTP
Farmers connect to your phone's IP when you're online
"""
from flask import Flask, request, jsonify
import subprocess, os

app = Flask(__name__)
MODEL = os.path.expanduser("~/vedic_model_q2.gguf")
LLAMA = os.path.expanduser("~/llama-b9297/llama-cli")
LLAMA_LIB = os.path.expanduser("~/llama-b9297")

@app.route('/llm')
def llm():
    q = request.args.get('q', 'Best crop for Assam?')
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = LLAMA_LIB
    
    proc = subprocess.Popen(
        [LLAMA, "-m", MODEL, "-p", q, "-n", "80", "--temp", "0.7",
         "--log-disable", "--no-display-prompt", "-c", "256"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, env=env
    )
    proc.stdin.write(q + "\n/exit\n")
    proc.stdin.flush()
    
    output = []
    for line in proc.stdout:
        s = line.strip()
        if s.startswith(">"):
            output.append(s[1:].strip())
        if len(output) > 5:
            break
    
    proc.terminate()
    return jsonify({"advice": "\n".join(output), "engine": "vedic-slm"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
