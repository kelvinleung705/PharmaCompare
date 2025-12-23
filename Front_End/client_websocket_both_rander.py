from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymongo
import certifi

import base64
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

file = None
client_id = None
pharmacies = None




@app.route('/', methods=['POST', 'GET'])
def index():
    image_data = None
    google_geocoding_api_key = os.getenv("Google_Geocoding_API_KEY")

    if request.method == 'POST':
        file = request.files['image']
        if file:
            image_read_stream = file.read()
            image_encoded = base64.b64encode(image_read_stream).decode('utf-8')
            image_type = file.content_type  # e.g., image/png
            image_data = f'data:{image_type};base64,{image_encoded}'
    return render_template('uploadImageWebSocket.html', image_data=image_data, google_map_api=google_geocoding_api_key)

@app.route('/api/pharmacies')
def get_all_pharmacies():
    # Load credentials securely from environment variables
    mongoDB_Username = os.getenv("MongoDB_Username")
    mongoDB_Password = os.getenv("MongoDB_Password")

    # Construct the connection string
    connection_string = (
        f"mongodb+srv://{mongoDB_Username}:{mongoDB_Password}"
        "@pharmacomparedata1.tu3p29k.mongodb.net/"
        "?retryWrites=true&w=majority&appName=PharmaCompareData1"
    )

    try:
        # Establish connection to the MongoDB client
        mongoDBclient = pymongo.MongoClient(
            connection_string,
            tls=True,
            tlsCAFile=certifi.where()
        )

        # Select the database and collection
        database = mongoDBclient["Drug_Price"]
        pharmacy_collection = database["pharmacy_drug_list"]

        # Fetch all documents from the collection, excluding the '_id' field
        # The .find() returns a cursor, so we convert it to a list
        pharmacies = list(pharmacy_collection.find({}, {'_id': 0}))

        # Close the database connection as soon as we're done with it
        mongoDBclient.close()

        # *** THE FIX: Use jsonify to return the data ***
        return jsonify(pharmacies)

    except Exception as e:
        # It's good practice to handle potential connection errors
        print(f"An error occurred: {e}")
        # Return a JSON error message with a 500 Internal Server Error status
        return jsonify({"error": "Could not connect to the database."}), 500


if __name__ == "__main__":
    import os
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)