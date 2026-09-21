#!/usr/bin/env bash
python training/preprocessing.py
python training/feature_engineering.py
python training/train.py
python training/evaluate.py
uvicorn backend.app.main:app --reload
