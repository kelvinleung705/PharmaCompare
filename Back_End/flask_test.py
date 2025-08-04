import flask
from flask import render_template, url_for, request, redirect

app = flask.Flask(__name__)

@app.route('/a')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
