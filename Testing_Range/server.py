from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

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

httpd = HTTPServer(('0.0.0.0', 5001), SimpleHandler)
print("Listening on port 5001...")
httpd.serve_forever()
