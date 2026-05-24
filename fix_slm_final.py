"""Properly fix SLM engine — handle quotes correctly"""

with open('backend/core/slm_engine.py', 'r') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    # Fix: line with double-wrapped quotes from bad sed
    if '"os.environ.get(' in line or "'os.environ.get(" in line:
        # This is the broken line — extract what we need and rebuild
        # We know the correct values
        if 'LLAMA_BIN' in line or 'llama-completion' in line:
            line = '        os.environ.get("LLAMA_BIN", os.path.expanduser("~/llama.cpp/build/bin/llama-completion"))\n'
        elif 'GGUF_MODEL' in line or 'vedic-krishi' in line:
            line = '        os.environ.get("GGUF_MODEL", os.path.expanduser("~/vedic-krishi-135m-q4.gguf"))\n'
    
    # Fix: remove the outer os.path.expanduser if LLAMA_BIN/GGUF_MODEL are already wrapped
    if 'LLAMA_BIN = os.path.expanduser(' in line and 'os.environ.get' not in line:
        line = '    LLAMA_BIN = os.environ.get("LLAMA_BIN", os.path.expanduser("~/llama.cpp/build/bin/llama-completion"))\n'
    if 'GGUF_MODEL = os.path.expanduser(' in line and 'os.environ.get' not in line:
        line = '    GGUF_MODEL = os.environ.get("GGUF_MODEL", os.path.expanduser("~/vedic-krishi-135m-q4.gguf"))\n'
    
    fixed_lines.append(line)

with open('backend/core/slm_engine.py', 'w') as f:
    f.writelines(fixed_lines)

print("✅ Fixed. Verifying...")

import py_compile
try:
    py_compile.compile('backend/core/slm_engine.py', doraise=True)
    print("✅ SYNTAX VALID!")
except py_compile.PyCompileError as e:
    print(f"❌ Still broken at line {e.lineno}: {e.msg}")
    # Show the problematic line
    with open('backend/core/slm_engine.py') as f:
        bad_lines = f.readlines()
    if e.lineno:
        print(f"   Line {e.lineno}: {bad_lines[e.lineno-1].rstrip()}")
