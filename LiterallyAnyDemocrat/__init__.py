import os, flask, requests
from . import data

app = flask.Flask(__name__)

STATES = data.load_states(os.environ['STATES_CSV_URL'])
CANDIDATES = data.load_candidates(os.environ['CANDIDATES_CSV_URL'])

@app.route('/')
def get_index():
    return flask.render_template('index.html', candidates_url=flask.url_for('get_candidates_json'))

@app.route('/candidates.json')
def get_candidates_json():
    a_candidate = CANDIDATES[0]
    a_state = STATES[(a_candidate.state, a_candidate.chamber)]

    return flask.jsonify({
        'head': list(a_candidate._fields) + list(a_state._fields),
        'rows': [
        list(c) + list(STATES[(c.state, c.chamber)]) for c in CANDIDATES
        ]})
