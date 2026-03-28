#!/usr/bin/python3
"""
API endpoint to summarize text
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TextRequest(BaseModel):
    text: str


@router.post("/summarize")
def summarize_text(request: TextRequest):
    """
    Simple summarization endpoint (stub function)
    """
    # Replace with actual summarization logic
    summary = " ".join(request.text.split()[:20]) + "..."
    return {"summary": summary}
