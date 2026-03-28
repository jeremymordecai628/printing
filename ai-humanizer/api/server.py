#!/usr/bin/python3
"""
Secure Payment Server
- WebSocket connection
- Initiate payment (server handles STK push)
- Store mapping (checkoutID → clientId)
- Handle callback
- Push result to correct client
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict


# =========================
# Storage (replace with DB in production)
# =========================

# clientId → WebSocket
active_connections: Dict[str, WebSocket] = {}

# checkoutRequestID → clientId
payment_db: Dict[str, str] = {}


# =========================
# 1. WebSocket
# =========================
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    print(f"{client_id} connected")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.pop(client_id, None)
        print(f"{client_id} disconnected")


# =========================
# 2. Initiate Payment
# =========================
@router.post("/initiate-payment")
async def initiate_payment(payload: dict):
    """
    Expected from client:
    {
        "phone": "2547xxxxxxx",
        "amount": "100",
        "clientId": "user123",
        "accountReference": "optional"
    }
    """

    phone = payload.get("phone")
    amount = payload.get("amount")
    client_id = payload.get("clientId")
    account_ref = payload.get("accountReference", "N/A")

    # 🔹 Generate checkout ID (replace with real STK response)
    checkout_id = str(uuid.uuid4())

    # 🔹 Store mapping
    payment_db[checkout_id] = client_id

    print(f"[PAYMENT CREATED]")
    print(f"Phone: {phone}, Amount: {amount}")
    print(f"CheckoutID: {checkout_id} → Client: {client_id}")

    # 🔹 TODO: Call real M-Pesa STK Push here

    return {
        "checkoutRequestID": checkout_id,
        "status": "PENDING"
    }


# =========================
# 3. Callback (M-Pesa)
# =========================
@router.post("/callback")
async def mpesa_callback(payload: dict):
    """
    Example callback:
    {
        "checkoutRequestID": "...",
        "result": "SUCCESS"
    }
    """

    checkout_id = payload.get("checkoutRequestID")
    result = payload.get("result")

    print(f"[CALLBACK] {checkout_id} → {result}")

    # 🔹 Find client
    client_id = payment_db.get(checkout_id)

    if not client_id:
        print("No mapping found")
        return {"status": "no mapping"}

    # 🔹 Find WebSocket
    websocket = active_connections.get(client_id)

    if not websocket:
        print("Client not connected")
        return {"status": "client offline"}

    # 🔹 Send result to client
    await websocket.send_json({
        "checkoutRequestID": checkout_id,
        "status": result
    })

    print(f"Sent result to {client_id}")

    return {"status": "sent"}


