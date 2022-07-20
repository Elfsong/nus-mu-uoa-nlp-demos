# coding: utf-8

# Author: Mingzhe Du
# Date: 2022-07-20
# Email: mingzhe@nus.edu.sg

from flask import Blueprint, request, abort, render_template
from flask_socketio import emit
from .. import socketio
from . model import QGModel

# Model object
qg_model = QGModel()

# Flask handler
socratic_qg = Blueprint('socratic_qg', __name__, template_folder='./templates', static_folder='./static')

@socratic_qg.route('/')
def index():
    return render_template('socratic_qg/index.html')

@socketio.on('generate', namespace='/socratic_qg')
def on_generate(data):
    client_id = request.sid
    input_context = data["context"]

    result = qg_model.generate_all_labels(input_context)

    for label in result:
        for question in result[label]:
            emit('update', {"topic": label, "question": question}, broadcast=False, namespace="/socratic_qg", room=client_id)
        