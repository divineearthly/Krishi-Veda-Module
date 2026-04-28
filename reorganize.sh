
#!/bin/bash

REPO_ROOT="$(dirname "$0")"
VEDIC_CORE_DIR="$REPO_ROOT/vedic_core"

# Ensure vedic_core directory exists
if [ ! -d "$VEDIC_CORE_DIR" ]; then
    echo "Error: $VEDIC_CORE_DIR not found." >&2
    exit 1
fi

# Create subdirectories if they don't exist
mkdir -p "$VEDIC_CORE_DIR/tests"
mkdir -p "$VEDIC_CORE_DIR/benchmarks"
mkdir -p "$VEDIC_CORE_DIR/demos"

echo "Created vedic_core/tests, vedic_core/benchmarks, vedic_core/demos directories."

# Move files to their respective new locations
# Assuming vedic_kernels.cpp is the main implementation
# and vedic_kernels_wasm.cpp might be a WebAssembly specific demo/target

if [ -f "$VEDIC_CORE_DIR/vedic_kernels.cpp" ]; then
    mv "$VEDIC_CORE_DIR/vedic_kernels.cpp" "$VEDIC_CORE_DIR/demos/"
    echo "Moved vedic_kernels.cpp to vedic_core/demos/"
fi

if [ -f "$VEDIC_CORE_DIR/vedic_kernels_wasm.cpp" ]; then
    mv "$VEDIC_CORE_DIR/vedic_kernels_wasm.cpp" "$VEDIC_CORE_DIR/demos/"
    echo "Moved vedic_kernels_wasm.cpp to vedic_core/demos/"
fi

# Assuming Makefile is for building the core, place it in demos for now if it's related to the demo build
if [ -f "$VEDIC_CORE_DIR/Makefile" ]; then
    mv "$VEDIC_CORE_DIR/Makefile" "$VEDIC_CORE_DIR/demos/"
    echo "Moved Makefile to vedic_core/demos/"
fi

echo "Reorganization complete."
