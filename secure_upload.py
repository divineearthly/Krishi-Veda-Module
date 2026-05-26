import os
import sys
from huggingface_hub import HfApi

repo_id = "divinesouljoy/Vedic-Transformer-Core"

# Dynamic path discovery array
paths_to_check = [
    "vedic_model_q2.gguf",
    os.path.expanduser("~/vedic_model_q2.gguf"),
    os.path.expanduser("~/llama-b9297/vedic_model_q2.gguf")
]

file_path = None
for path in paths_to_check:
    if os.path.exists(path) and os.path.isfile(path):
        file_path = path
        break

if not file_path:
    print("[!] Error: 'vedic_model_q2.gguf' could not be found anywhere on your device.")
    print("Please double check your file name or location.")
    sys.exit(1)

print(f"🟢 Located quantized model file at: {file_path}")
print(f"⚡ Initializing robust LFS stream to huggingface.co/{repo_id}...")

api = HfApi()

try:
    response = api.upload_file(
        path_or_fileobj=file_path,
        path_in_repo="vedic_model_q2.gguf",
        repo_id=repo_id,
        repo_type="model"
    )
    print("\n✅ SUCCESS! The main Vedic core model is anchored to your cloud registry.")
    print(f"Secure Repository Link: {response}")
except Exception as e:
    print(f"\n[!] Stream Exception Intercepted: {e}")
    print("If this is a network timeout, try uploading via your mobile web browser interface.")
