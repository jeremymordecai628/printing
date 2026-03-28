#!/usr/bin/python3
"""
Dataset loader for humanization task.
"""

import torch
from torch.utils.data import Dataset


class HumanizerDataset(Dataset):
    """
    Dataset for mapping AI text → human text.
    """

    def __init__(self, inputs, targets):
        self.inputs = inputs
        self.targets = targets

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, idx):
        return (
            torch.tensor(self.inputs[idx]),
            torch.tensor(self.targets[idx])
        )
