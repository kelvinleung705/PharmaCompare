from flask import Flask, render_template, request, redirect, url_for, session
from flask import Flask, render_template_string, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import base64
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
    return render_template('uploadImageWebSocketLocal.html', image_data=image_data)

"""
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
"""

"""
@app.route('/client_id_set', methods=['POST'])
def set_client_id():
    data = request.get_json()
    if not data or 'client_id' not in data:
        return 'No client_id provided', 400
    global client_id
    client_id = data['client_id']
    return f"Client ID set to: {client_id}", 200
"""

"""
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
        'file': (image_name, image_file, file_type)  # name, content, MIME type
    }
    client_id_from_request = data.get('localClientId')
    if not client_id_from_request:
        return 'No client_id provided in the request', 400

    try:
        response = requests.post('http://127.0.0.1:5001/upload/' + client_id_from_request, files=files)
        # 2. CHECK THE STATUS CODE (Good Practice)
        # This confirms the request was accepted as expected.
        response.raise_for_status()  # This will raise an exception for 4xx or 5xx errors
        # 3. GET THE JSON RESPONSE
        # The .json() method parses the response body into a Python dictionary.
        data = response.json()
        status_code = response.status_code
        if  status_code == 202:
            return data.get('message'), status_code
        else:
            return 'Image invalid', 200
    # Send to external Flask server
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        # You might want to see the error body from the server
        print(f"Server response: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"An other error occurred: {err}")
"""
"""
    finally:
        # Clean up the dummy file
        os.remove(file_to_upload)
"""





if __name__ == '__main__':
    print("Starting WebSocket server on http://localhost:5000")
    http_server = WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
