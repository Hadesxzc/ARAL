#!/usr/bin/env bash
set -e

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BACKEND_DIR"

echo "=== ARAL Backend Startup ==="

# Train model if not already trained
MODEL_FILE="model/aral_model.pkl"
if [ ! -f "$MODEL_FILE" ]; then
  echo "Training ARAL model (first run — takes ~30s)..."
  python3 -c "from model.train import train_and_save; train_and_save()"
  echo "Model training complete."
else
  echo "Model already trained — skipping."
fi

# Start the FastAPI server
echo "Starting ARAL FastAPI server on port ${PORT:-8080}..."
exec python3 -m uvicorn main:app --host 0.0.0.0 --port "${PORT:-8080}" --reload
