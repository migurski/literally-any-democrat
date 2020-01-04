import flask

app = flask.Flask(__name__)

@app.route('/')
def get_index():
    return 'Yo'
