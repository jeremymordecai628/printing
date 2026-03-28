#!/usr/bin/python3
"""
Evaluation module.

Evaluates model performance.
"""

import joblib
import pandas as pd
from sklearn.metrics import classification_report

from feature_engineering import extract_features


def evaluate():
    """Evaluate trained model."""
    model = joblib.load("../models/humanizer_model.pkl")
    df = pd.read_csv("../data/splits/test.csv")

    X = df["text"].apply(extract_features).tolist()
    y = df["label"]

    predictions = model.predict(X)

    print(classification_report(y, predictions))


if __name__ == "__main__":
    evaluate()
