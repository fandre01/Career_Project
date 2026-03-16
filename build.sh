#!/usr/bin/env bash
set -o errexit

# Install Python dependencies
pip install -r backend/requirements.txt

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Run database seed if needed
python -m scripts.seed_database 2>/dev/null || true
python -m scripts.train_models 2>/dev/null || true
