
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import os

import app
from dotenv import load_dotenv

from Testing_Range.add_pharmacy_drug_receipt import new_pharmacy_drug_receipt
from Testing_Range.pharmacy_receipt_byte import pharmacy_receipt_byte

from fastapi import FastAPI, WebSocket, UploadFile, File, WebSocketDisconnect
import uvicorn  # The ASGI server to run our app
import websockets


from fastapi.responses import JSONResponse
import asyncio
from typing import Dict
import uuid




app = FastAPI()
active_connections: Dict[str, WebSocket] = {}

async def process_image(file_data, client_id):
    load_dotenv()
    access_key_id = os.getenv("AWS_Access_Key")
    secret_access_key = os.getenv("AWS_Secret_Access_Key")
    receipt_byte = pharmacy_receipt_byte(access_key_id, secret_access_key, file_data)
    valid = receipt_byte.extract_and_access()
    if valid:
        mongoDB_Username = os.getenv("MongoDB_Username")
        mongoDB_Password = os.getenv("MongoDB_Password")
        new_pharmacy_drug = new_pharmacy_drug_receipt(receipt_byte, mongoDB_Username, mongoDB_Password)
        new_pharmacy_drug.add_pharmacy_drug()
        print("Adding drug done")
        if client_id in active_connections.keys():
            await active_connections[client_id].send_json({'type': 'update', 'data': 'image valid'})
    else:
        if client_id in active_connections.keys():
            await active_connections[client_id].send_json({'type': 'update', 'data': 'image invalid'})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    client_id = str(uuid.uuid4())
    active_connections[client_id] = websocket

    await websocket.send_json({'type':'client_id', 'data':client_id})

    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        pass
    finally:
        del active_connections[client_id]


@app.post("/upload/{client_id}")
async def upload_image(client_id: str, file: UploadFile = File(...)):

    file_data = await file.read()

    # Save file
    with open(f"received_image", "wb") as f:
        f.write(file_data)

    """result = await asyncio.to_thread(process_image, file_data, client_id)"""
    await process_image(file_data, client_id)
    """return {"message": "File received"}send json back"""
    await active_connections[client_id].send_json({'type': 'update', 'data': 'image received'})



if __name__ == "__main__":
    print("Starting FastAPI server with Uvicorn on http://0.0.0.0:5001")
    # This command starts the ASGI server, which will keep listening for
    # both HTTP and WebSocket connections indefinitely.
    uvicorn.run(app, host="0.0.0.0", port=5001)
