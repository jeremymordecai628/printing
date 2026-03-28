#!/usr/bin/python3
"""
Feature engineering module.

Converts text into numerical features for ML models.
"""

import numpy as np
import re


def sentence_lengths(text):
    """Return list of sentence lengths."""
    sentences = re.split(r'[.!?]+', text)
    return [len(s.split()) for s in sentences if s.strip()]


def lexical_diversity(text):
    """Compute type-token ratio."""
    words = text.split()
    if not words:
        return 0
    return len(set(words)) / len(words)


def avg_sentence_length(text):
    """Compute average sentence length."""
    lengths = sentence_lengths(text)
    return np.mean(lengths) if lengths else 0


def variance_sentence_length(text):
    """Compute variance of sentence length."""
    lengths = sentence_lengths(text)
    return np.var(lengths) if lengths else 0


def extract_features(text):
    """
    Convert text into feature vector.

    Returns:
        list: numerical features
    """
    return [
        lexical_diversity(text),
        avg_sentence_length(text),
        variance_sentence_length(text),
        len(text.split())
    ]
