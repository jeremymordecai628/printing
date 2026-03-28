#!/usr/bin/python3
"""
API endpoint to humanize AI-generated text
"""

from fastapi import APIRouter
from pydantic import BaseModel
from inference.rewrite import rewrite_text
from api.model_loader import model, tokenizer
import torch

router = APIRouter()

class TextRequest(BaseModel):
    text: str


@router.post("/humanize")
def humanize_text(request: TextRequest):
    """
    Rewrite AI-generated text into human-like text.
    """
    with torch.no_grad():
        output = rewrite_text(model, tokenizer, request.text)
    return {"humanized_text": output}
