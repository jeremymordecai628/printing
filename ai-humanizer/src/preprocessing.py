#!/usr/bin/python3
"""
Preprocessing module.

Handles:
- Cleaning text
- Merging datasets
- Creating labeled dataset
"""

import pandas as pd
import re


def clean_text(text):
    """Clean and normalize text."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def load_and_merge(ai_path, human_path, output_path):
    """
    Merge AI and human datasets into one labeled dataset.

    Args:
        ai_path (str): path to AI text CSV
        human_path (str): path to human text CSV
        output_path (str): where to save merged dataset
    """
    ai_df = pd.read_csv(ai_path)
    human_df = pd.read_csv(human_path)

    ai_df["label"] = 0
    human_df["label"] = 1

    df = pd.concat([ai_df, human_df], ignore_index=True)

    df["text"] = df["text"].apply(clean_text)

    df.to_csv(output_path, index=False)
    print(f"Dataset saved to {output_path}")
