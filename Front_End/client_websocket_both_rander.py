from flask import Flask, render_template, request, redirect, url_for, session
from flask import Flask, render_template_string, request

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
    return render_template('uploadImageWebSocket.html', image_data=image_data)


if __name__ == "__main__":
    import os
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)