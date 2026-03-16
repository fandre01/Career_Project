#!/usr/bin/env python3
"""Seed the database with career data."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db.seed import seed_database

if __name__ == "__main__":
    seed_database()
