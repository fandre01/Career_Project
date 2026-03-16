#!/usr/bin/env python3
"""Train ML models and generate predictions."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ml.pipeline import train_and_evaluate

if __name__ == "__main__":
    train_and_evaluate()
