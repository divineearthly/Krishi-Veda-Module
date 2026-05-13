FROM python:3.11-slim-bookworm AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim-bookworm
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
RUN pip install --no-cache-dir bitsandbytes-cpu
ENV PATH=/root/.local/bin:$PATH
ENV KRISHI_MODE=edge
ENV OFFLINE_DB_PATH=/data/krishi_veda_offline.db
VOLUME ["/data"]
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
