# Krishi-Veda Configuration
# ARM64 Termux optimized

# Paths
LLAMA_BIN = "/root/llama.cpp/build/bin/llama-simple"
GGUF_MODEL = "/data/data/com.termux/files/home/vedic_model.gguf"
VEDIC_KERNELS = "vedic_engine/kernels/vedic_kernels.so"

# Assam Silchar coordinates
DEFAULT_LAT = 24.81
DEFAULT_LON = 92.80

# Model settings
MAX_NEW_TOKENS = 220
TEMPERATURE = 0.7
CTX_SIZE = 512

# Ahimsa-108 Protocol
AHIMSA_THRESHOLD = 75.0
CHEMICAL_BLOCK_LIST = ["urea", "dap", "mop", "superphosphate", "pesticide", "herbicide"]

# Languages
LANGUAGES = ["english", "hindi", "bengali", "assamese"]
DEFAULT_LANG = "english"

# Crop database (Assam region)
CROPS = ["rice", "jute", "mustard", "vegetables", "tea", "bamboo"]
