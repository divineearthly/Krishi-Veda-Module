# Use Python 3.12 slim image
FROM python:3.12-slim

# Install C++ compiler for Vedic Kernels
RUN apt-get update && apt-get install -y g++ && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python requirements
# Note: Ensure you have a requirements.txt in the folder
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Compile C++ Vedic Kernels during build
RUN g++ -O3 -shared -fPIC -o Krishi-Veda-Module/cpp_kernels/libvedic_v2.so Krishi-Veda-Module/cpp_kernels/vedic_v2.cpp

# Expose the API port
EXPOSE 8000

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
