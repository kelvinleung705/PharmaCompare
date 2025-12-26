
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import os

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from add_pharmacy_drug_receipt import new_pharmacy_drug_receipt
from pharmacy_receipt_byte import pharmacy_receipt_byte

from fastapi import FastAPI, WebSocket, UploadFile, File, WebSocketDisconnect, BackgroundTasks
import uvicorn  # The ASGI server to run our app



from fastapi.responses import JSONResponse
import asyncio
from typing import Dict
import uuid




app = FastAPI()
active_connections: Dict[str, WebSocket] = {}

# =======================================================================
# THIS IS THE FIX
# =======================================================================
origins = [
    # The origin from your network log that needs permission
    "http://localhost:5000",

    # The URL of your frontend running on Heroku, Render
    "https://pharmacompare-7e5413777c20.herokuapp.com",
    "https://pharmacompare-client-server.onrender.com",

    # It's good practice to also include these for flexibility
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # The list of origins that are allowed to make requests
    allow_credentials=True,      # Allow cookies to be sent
    allow_methods=["*"],         # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],         # Allow all headers
)
# =======================================================================

def process_image_sync(file_data, client_id):
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
        return {'type': 'update', 'data': 'image valid'}
    else:
        return {'type': 'update', 'data': 'image invalid'}

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

async def process_image_async(file_data: bytes, client_id: str):
    try:
        # Run the blocking code in a separate thread
        result = await asyncio.to_thread(process_image_sync, file_data, client_id)
        print("process done")
        # Send the result using the async WebSocket function
        if client_id in active_connections:
            print("confirm message sending")

            await active_connections[client_id].send_json({'type': 'update', 'data': result['data']})
    except Exception as e:
        print(f"Error during processing for {client_id}: {e}")
        if client_id in active_connections:
            print("confirm message sending")
            await active_connections[client_id].send_json({'type': 'update', 'data': 'Processing failed.'})

@app.post("/upload/{client_id}")
async def upload_image(client_id: str,  background_tasks: BackgroundTasks, file: UploadFile = File(...)):

    file_data = await file.read()

    # Save file
    with open(f"received_image", "wb") as f:
        f.write(file_data)

    background_tasks.add_task(process_image_async, file_data, client_id)
    """await process_image(file_data, client_id)"""
    return JSONResponse(
        status_code=202,
        content={"message": "Upload accepted. Processing in background. Watch for WebSocket updates."}
    )




if __name__ == "__main__":

    print("Starting FastAPI server with Uvicorn on http://0.0.0.0:5001")
    # This command starts the ASGI server, which will keep listening for
    # both HTTP and WebSocket connections indefinitely.
    uvicorn.run(app, host="0.0.0.0", port=5001)
