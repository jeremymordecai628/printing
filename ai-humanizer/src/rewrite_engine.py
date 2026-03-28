#!/usr/bin/python3
"""
Rewrite engine (WordNet-based).

Responsibilities:
- Generate multiple human-like variations
- Use dynamic synonym replacement
- Maintain reasonable grammatical structure
"""

import random
import re
from nltk.corpus import wordnet


def get_synonyms(word):
    """
    Fetch synonyms for a word using WordNet.

    Args:
        word (str)

    Returns:
        list: synonyms
    """
    synonyms = set()

    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            name = lemma.name().replace("_", " ").lower()

            # Avoid identical replacements
            if name != word:
                synonyms.add(name)

    return list(synonyms)


def synonym_replace(text, replace_prob=0.3):
    """
    Replace words with synonyms dynamically.

    Args:
        text (str)
        replace_prob (float): probability of replacement

    Returns:
        str
    """
    words = text.split()
    new_words = []

    for word in words:
        clean_word = re.sub(r'[^\w]', '', word).lower()

        # Decide whether to replace
        if random.random() < replace_prob:
            synonyms = get_synonyms(clean_word)

            if synonyms:
                replacement = random.choice(synonyms)
                new_words.append(replacement)
                continue

        new_words.append(word)

    return " ".join(new_words)


def sentence_variation(text):
    """
    Slightly vary sentence structure.

    Methods:
    - Shuffle sentence order
    - Keep structure mostly intact

    Args:
        text (str)

    Returns:
        str
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) > 1:
        random.shuffle(sentences)

    return ". ".join(sentences) + "."


def punctuation_variation(text):
    """
    Add slight punctuation variation.

    Args:
        text (str)

    Returns:
        str
    """
    # Example: replace some commas with semicolons
    return re.sub(r',', lambda _: random.choice([",", ";"]), text)


def generate_variants(text, n=5):
    """
    Generate multiple rewritten versions.

    Args:
        text (str)
        n (int): number of variants

    Returns:
        list[str]
    """
    variants = []

    for _ in range(n):
        v = text

        # Apply transformations in sequence
        v = synonym_replace(v, replace_prob=0.3)
        v = sentence_variation(v)
        v = punctuation_variation(v)

        variants.append(v)

    return variants
