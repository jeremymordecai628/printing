#!/usr/bin/python3
"""
Basic tokenizer (replace with HuggingFace later).
"""

class SimpleTokenizer:
    """
    Converts text to integer tokens.
    """

    def __init__(self):
        self.word2idx = {}
        self.idx2word = {}

    def fit(self, texts):
        vocab = set()
        for text in texts:
            vocab.update(text.split())

        self.word2idx = {w: i+1 for i, w in enumerate(vocab)}
        self.idx2word = {i: w for w, i in self.word2idx.items()}

    def encode(self, text):
        return [self.word2idx.get(w, 0) for w in text.split()]

    def decode(self, tokens):
        return " ".join([self.idx2word.get(t, "<unk>") for t in tokens])
