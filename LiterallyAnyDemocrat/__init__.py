import os, flask, requests
from . import data

app = flask.Flask(__name__)

STATES = data.load_states(os.environ['STATES_CSV_URL'])
CANDIDATES = data.load_candidates(os.environ['CANDIDATES_CSV_URL'])

@app.route('/')
def get_index():
    return flask.render_template('index.html',
        states_url=flask.url_for('get_states_json'),
        candidates_url=flask.url_for('get_candidates_json'))

@app.route('/candidates.json')
def get_candidates_json():
    a_candidate = CANDIDATES[0]
    a_state = STATES[(a_candidate.state, a_candidate.chamber)]

    return flask.jsonify({
        'head': list(a_candidate._fields) + list(a_state._fields[2:-1]),
        'rows': [
        list(c) + list(STATES[(c.state, c.chamber)][2:-1]) for c in CANDIDATES
        ]})

@app.route('/states.json')
def get_states_json():
    a_candidate = CANDIDATES[0]
    a_state = STATES[(a_candidate.state, a_candidate.chamber)]

    return flask.jsonify({
        'head': list(a_state._fields),
        'rows': [list(s) for s in STATES.values()],
        })
