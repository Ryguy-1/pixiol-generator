# Use the official NVIDIA CUDA base image as the base image
FROM nvidia/cuda:11.0-base

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies and prerequisites
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl https://ollama.ai/install.sh | sh

# Pull the "mistral-openorca" repository
RUN ollama pull mistral-openorca

# Copy your requirements.txt file into the container
COPY requirements.txt .

# Install Python packages from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy your Python source code into the container
COPY src/ ./src/

# Define the entry point command to run your Python script
CMD ["python3", "./src/main.py"]
