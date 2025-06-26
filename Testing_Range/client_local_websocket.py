import requests
from flask import Flask, render_template, request, redirect, url_for, session
from flask import Flask, render_template_string, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from datetime import datetime
import os
import base64
import io
import re
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)

file = None
client_id = None


@app.route('/', methods=['POST', 'GET'])
def index():
    image_data = None
    if request.method == 'POST':
        file = request.files['image']
        if file:
            image_read_stream = file.read()
            image_encoded = base64.b64encode(image_read_stream).decode('utf-8')
            image_type = file.content_type  # e.g., image/png
            image_data = f'data:{image_type};base64,{image_encoded}'
    return render_template('uploadImage.html', image_data=image_data)

@app.route('/ws')
def ws_handler():
    ws = request.environ.get('wsgi.websocket')  # Get the WebSocket object
    if not ws:
        return "WebSocket connection expected", 400  # If it's not a WS request

    while True:
        try:
            message = ws.receive()
            if message is None:
                break  # Client disconnected
            print(f"Client sent raw message: {message}")
            # Parse JSON string into dict
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                ws.send("Error: Invalid JSON format")
                continue

            # Now safely access data fields
            if data.get('type') == 'client_id':
                global client_id
                client_id = data.get('data')
                print(f"Received client_id: {client_id}")
            elif data.get('type') == 'update':
                print(f"Received update: {data.get('data')}")

            # Optionally send acknowledgement
            ws.send("Message processed")
        except Exception as e:
            print("WebSocket error:", e)
            break
    return ''

@app.route('/submit', methods=['POST'])
def send_image():
    data = request.get_json()
    if not data or 'image_base64' not in data:
        return 'No image data provided', 400

    image_base64 = data['image_base64']

    # image_base64 is like "data:image/png;base64,iVBORw0KGgoAAAANS..."
    # You want to strip the prefix before decoding:
    header, encoded = image_base64.split(',', 1)

    file_type = header.split(';')[0].split(':')[1]

    image_type = file_type.split('/', 1)[1]

    image_name = "receipt." + image_type

    try:
        image_bytes = base64.b64decode(encoded)
    except Exception as e:
        return f'Invalid base64 data: {str(e)}', 400
    image_file = io.BytesIO(image_bytes)
    files = {
        'image': (image_name, image_file, file_type)  # name, content, MIME type
    }

    response = requests.post('http://127.0.0.1:5001/upload/' + client_id, files=files)
    if response.content == b'File received, file is valid':
        return 'Image received successfully', 200
    else:
        return 'Image invalid', 200
    # Send to external Flask server




if __name__ == '__main__':
    print("Starting WebSocket server on http://localhost:5000")
    http_server = WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
