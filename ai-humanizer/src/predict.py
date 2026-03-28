#!/usr/bin/python3
"""
Prediction module.

Selects most human-like version of text.
"""

import joblib
from feature_engineering import extract_features
from rewrite_engine import generate_variants


def humanize(text):
    """Return best human-like version."""
    model = joblib.load("../models/humanizer_model.pkl")

    variants = generate_variants(text, n=5)

    best_score = -1
    best_text = text

    for v in variants:
        features = [extract_features(v)]
        score = model.predict_proba(features)[0][1]

        if score > best_score:
            best_score = score
            best_text = v

    return best_text


if __name__ == "__main__":
    sample = "This study shows many important results."
    print(humanize(sample))
