#!/bin/bash
# Jennifer Eye 👁️ — start script
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "🔧 Venv aanmaken..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install rumps requests
else
    source .venv/bin/activate
fi

echo "👁️ Jennifer Eye starten..."
python3 jennifer_eye.py
