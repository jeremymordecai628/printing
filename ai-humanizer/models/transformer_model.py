#!/usr/bin/python3
"""
Transformer model for AI text humanization.
"""

import torch
import torch.nn as nn


class HumanizerModel(nn.Module):
    """
    Encoder-Decoder Transformer for paraphrasing AI-generated text.
    """

    def __init__(self, vocab_size, d_model=256, nhead=8, num_layers=3):
        super(HumanizerModel, self).__init__()

        self.embedding = nn.Embedding(vocab_size, d_model)

        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=nhead,
            num_encoder_layers=num_layers,
            num_decoder_layers=num_layers
        )

        self.fc_out = nn.Linear(d_model, vocab_size)

    def forward(self, src, tgt):
        src = self.embedding(src)
        tgt = self.embedding(tgt)

        output = self.transformer(src, tgt)
        return self.fc_out(output)
