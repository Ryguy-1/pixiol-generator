#!/bin/bash

# === Config ===
if [ ! -f src/config.py ]; then
    echo "ERROR: Must Create 'src/config.py' file. Example:"
    cat src/config.sample.py
    exit 1
fi

# === Background Tasks ===
ollama serve >/dev/null 2>&1 &

# === Main ===
python3 src/main.py
