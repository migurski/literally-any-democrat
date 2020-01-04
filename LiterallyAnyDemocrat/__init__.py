import os, flask, requests
from . import data

app = flask.Flask(__name__)

@app.route('/')
def get_index():
    return 'Yo'
