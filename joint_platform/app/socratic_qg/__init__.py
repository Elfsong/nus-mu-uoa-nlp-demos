# coding: utf-8

# Author: Mingzhe Du
# Date: 2022-07-20
# Email: mingzhe@nus.edu.sg

from flask import Blueprint, request, abort, render_template
from flask_socketio import emit
from .. import socketio
from . model import QG_Model

# Model object
qg_model = QG_Model()

# Flask handler
socratic_qg = Blueprint('socratic_qg', __name__, template_folder='./templates', static_folder='./static')

@socratic_qg.route('/')
def index():
    return render_template('socratic_qg/index.html')

@socketio.on('generate', namespace='/socratic_qg')
def on_generate(data):
    client_id = request.sid
    context = data["context"]

    total_count, processed_count = len(qg_model.labels), 0
    
    for label, repetition_penalty, temperature, sample_size in zip(qg_model.labels, qg_model.repetition_penalties, qg_model.temperatures, qg_model.sample_sizes):
        results = qg_model.generate(label = label, context=context, sample_size=sample_size, repetition_penalty=repetition_penalty, temperature=temperature)
        processed_count += 1
        emit('update', {"topic": label, "results": results, "total": total_count, "current": processed_count}, broadcast=False, namespace="/socratic_qg", room=client_id)
        socketio.sleep(1)

        