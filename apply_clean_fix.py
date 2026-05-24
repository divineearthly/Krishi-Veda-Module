"""Apply the SLM path fix cleanly to the original file"""
import os

# Find the best source file
candidates = [
    'backend/core/slm_engine.py.backup',    # Original untouched backup
    'backend/core/slm_engine.py.backup2',   # Second backup
]

source = None
for c in candidates:
    if os.path.exists(c):
        # Test if it compiles
        try:
            import py_compile
            py_compile.compile(c, doraise=True)
            source = c
            print(f"✅ Found clean source: {c}")
            break
        except:
            print(f"❌ {c} is also broken")
            pass

if not source:
    print("⚠️ No clean backup found — checking git...")
    import subprocess
    result = subprocess.run(['git', 'log', '--oneline', '-5', '--', 'backend/core/slm_engine.py'], 
                          capture_output=True, text=True)
    print(result.stdout)
    # Try to get the original version from the first commit
    result = subprocess.run(['git', 'show', 'HEAD~3:backend/core/slm_engine.py'],
                          capture_output=True, text=True)
    if result.returncode == 0:
        with open('backend/core/slm_engine_original.py', 'w') as f:
            f.write(result.stdout)
        source = 'backend/core/slm_engine_original.py'
        print(f"✅ Restored from git")

if source:
    # Read the clean file
    with open(source, 'r') as f:
        content = f.read()
    
    # Make the fix: replace hardcoded paths with dynamic ones
    # Pattern: os.path.expanduser(\n        "/root/...")
    old_llama = 'os.path.expanduser(\n        "/root/llama.cpp/build/bin/llama-completion"'
    new_llama = 'os.environ.get("LLAMA_BIN", os.path.expanduser("~/llama.cpp/build/bin/llama-completion"))'
    
    old_gguf = 'os.path.expanduser(\n        "/root/vedic-krishi-135m-q4.gguf"'
    new_gguf = 'os.environ.get("GGUF_MODEL", os.path.expanduser("~/vedic-krishi-135m-q4.gguf"))'
    
    if old_llama in content:
        content = content.replace(old_llama, new_llama)
        content = content.replace(old_gguf, new_gguf)
        print("✅ Paths replaced")
    else:
        print("⚠️ Old pattern not found — checking what's there...")
        # Show lines around LLAMA_BIN
        for i, line in enumerate(content.split('\n')):
            if 'LLAMA_BIN' in line or 'GGUF_MODEL' in line or 'llama' in line.lower():
                print(f"  Line {i+1}: {line}")
    
    # Write the fixed file
    with open('backend/core/slm_engine.py', 'w') as f:
        f.write(content)
    
    # Verify syntax
    import py_compile
    try:
        py_compile.compile('backend/core/slm_engine.py', doraise=True)
        print("✅ SYNTAX VALID!")
    except py_compile.PyCompileError as e:
        print(f"❌ Failed: {e}")
        # Show the broken lines
        with open('backend/core/slm_engine.py') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if 'LLAMA' in line or 'GGUF' in line or 'llama' in line:
                print(f"  Line {i+1}: {line.rstrip()}")
else:
    print("❌ Could not find any clean source")
