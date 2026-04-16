#!/usr/bin/env bash
set -o errexit

# Bootstrap pip if not available (works on Railway/Nix environments)
python3 -m ensurepip --upgrade 2>/dev/null || curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Install Python dependencies
python3 -m pip install --upgrade pip
python3 -m pip install -r backend/requirements.txt

# Build frontend
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..

# Run database seed if needed (non-fatal if it fails)
python3 -m scripts.seed_database 2>/dev/null || true
python3 -m scripts.train_models 2>/dev/null || true
