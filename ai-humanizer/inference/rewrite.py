#!/usr/bin/python3
"""
Inference script to humanize text.
"""

import torch


def rewrite_text(model, tokenizer, text, max_len=50):
    """
    Generate human-like text from AI-generated input.
    """
    model.eval()

    tokens = tokenizer.encode(text)
    src = torch.tensor(tokens).unsqueeze(1)

    tgt = torch.zeros((1, 1), dtype=torch.long)

    for _ in range(max_len):
        output = model(src, tgt)
        next_token = output.argmax(-1)[-1, 0].item()

        tgt = torch.cat([tgt, torch.tensor([[next_token]])], dim=0)

    return tokenizer.decode(tgt.squeeze().tolist())
