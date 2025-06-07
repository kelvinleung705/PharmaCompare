from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
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



if __name__ == "__main__":
    import os
    app.run(debug=True, use_reloader=False)
