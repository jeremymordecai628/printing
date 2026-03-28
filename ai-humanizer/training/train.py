#!/usr/bin/python3
"""
Training script for humanizer model.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from models.transformer_model import HumanizerModel
from utils.dataset import HumanizerDataset


def train(model, dataloader, epochs=5):
    """
    Train the model.
    """
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()

    model.train()

    for epoch in range(epochs):
        total_loss = 0

        for src, tgt in dataloader:
            optimizer.zero_grad()

            output = model(src, tgt[:-1])
            loss = loss_fn(output.reshape(-1, output.shape[-1]), tgt[1:].reshape(-1))

            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch+1}, Loss: {total_loss}")
