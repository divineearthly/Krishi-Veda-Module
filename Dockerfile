FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        g++ \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN g++ -Os -fPIC -shared -std=c++14 \
        -o vedic_core/vedic_kernels.so \
        vedic_core/vedic_kernels.cpp \
        -lm && \
    mkdir -p vedic_engine/kernels && \
    cp vedic_core/vedic_kernels.so vedic_engine/kernels/vedic_kernels.so

ENV PORT=7860
EXPOSE 7860

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
