import re

with open('backend/core/slm_engine.py', 'r') as f:
    content = f.read()

# Fix the broken line — properly format the dynamic path
old_llama = 'os.path.expanduser(\n        os.environ.get("LLAMA_BIN", os.path.expanduser("~/llama.cpp/build/bin/llama-completion"))'
new_llama = 'os.environ.get("LLAMA_BIN", os.path.expanduser("~/llama.cpp/build/bin/llama-completion"))'

old_gguf = 'os.path.expanduser(\n        os.environ.get("GGUF_MODEL", os.path.expanduser("~/vedic-krishi-135m-q4.gguf"))'
new_gguf = 'os.environ.get("GGUF_MODEL", os.path.expanduser("~/vedic-krishi-135m-q4.gguf"))'

content = content.replace(old_llama, new_llama)
content = content.replace(old_gguf, new_gguf)

# Also fix config.py
try:
    with open('backend/config.py', 'r') as f:
        config = f.read()
    config = config.replace(
        'LLAMA_BIN = os.environ.get("LLAMA_BIN", os.path.expanduser("~/llama.cpp/build/bin/llama-completion"))',
        'LLAMA_BIN = os.environ.get("LLAMA_BIN", os.path.expanduser("~/llama.cpp/build/bin/llama-completion"))'
    )
    # Add import os if missing
    if 'import os' not in config:
        config = 'import os\n' + config
    with open('backend/config.py', 'w') as f:
        f.write(config)
    print("✅ config.py fixed")
except:
    pass

with open('backend/core/slm_engine.py', 'w') as f:
    f.write(content)

print("✅ slm_engine.py syntax fixed")

# Verify
import py_compile
try:
    py_compile.compile('backend/core/slm_engine.py', doraise=True)
    print("✅ Syntax valid!")
except py_compile.PyCompileError as e:
    print(f"❌ Still broken: {e}")
