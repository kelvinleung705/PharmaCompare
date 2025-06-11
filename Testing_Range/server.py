from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import os
from dotenv import load_dotenv

from Testing_Range.add_pharmacy_drug_receipt import new_pharmacy_drug_receipt
from Testing_Range.pharmacy_receipt_file import pharmacy_receipt_file
from Testing_Range.pharmacy_receipt_byte import pharmacy_receipt_byte


class SimpleHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Parse the multipart form data
        if self.path != '/upload':
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
            return
        content_type = self.headers.get('Content-Type')
        if not content_type.startswith('multipart/form-data'):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid content type")
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': content_type,
            }
        )

        file_field = form['image']
        filename = file_field.filename
        content_type = file_field.type
        file_data = file_field.file.read()

        # Save file
        with open(f"received_{filename}", "wb") as f:
            f.write(file_data)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"File received")

        load_dotenv()
        access_key_id = os.getenv("AWS_Access_Key")
        secret_access_key = os.getenv("AWS_Secret_Access_Key")
        receipt_byte = pharmacy_receipt_byte(access_key_id, secret_access_key, file_data)
        receipt_byte.extract_and_access()
        mongoDB_Username = os.getenv("MongoDB_Username")
        mongoDB_Password = os.getenv("MongoDB_Password")
        new_pharmacy_drug = new_pharmacy_drug_receipt(receipt_byte, mongoDB_Username, mongoDB_Password)
        new_pharmacy_drug.add_pharmacy_drug()
        print("Adding drug done")

httpd = HTTPServer(('0.0.0.0', 5001), SimpleHandler)
print("Listening on port 5001...")
httpd.serve_forever()
