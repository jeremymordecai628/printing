#!/usr/bin/python3
"""
Run FastAPI using python3 directly
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API running"}


