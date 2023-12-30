FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# === Workdir ===
WORKDIR /app

# === Install dependencies ===
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN curl https://ollama.ai/install.sh | sh

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# === Copy source code ===
COPY src/ ./src/

# === Run ===
COPY startup.sh .
RUN chmod +x startup.sh

CMD ["bash", "startup.sh"]
