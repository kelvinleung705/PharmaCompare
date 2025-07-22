# We import from Quart, the modern twin of Flask
from quart import Quart, render_template, request
import base64

# Quart automatically finds the 'templates' folder
app = Quart(__name__)


# A Quart route must be an 'async' function
@app.route('/', methods=['POST', 'GET'])
async def index():
    image_data = None
    if request.method == 'POST':
        # In Quart, you must 'await' file operations
        files = await request.files
        uploaded_file = files.get('image')

        if uploaded_file:
            image_read_stream = await uploaded_file.read()
            image_encoded = base64.b64encode(image_read_stream).decode('utf-8')
            image_type = uploaded_file.content_type
            image_data = f'data:{image_type};base64,{image_encoded}'

    # You must 'await' the template rendering
    return await render_template('uploadImageWebSocket.html', image_data=image_data)
