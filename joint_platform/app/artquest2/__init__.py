from flask import Blueprint, render_template, Response
from flask_socketio import emit
from .. import socketio
import json

import app.artquest2.model as model

artquest2 = Blueprint('artquest2', __name__, template_folder='./templates', static_folder='./static')

@artquest2.route('/')
def index():
    return render_template('artquest2/index.html')

@socketio.on('get_openning', namespace='/artquest2')
def get_openning(request):
    data = json.loads(request['data'])

    title = data['picture']["title"]
    author = data['picture']["author"]

    openning_sentence = model.get_openning_sentence(title, author)

    emit('receive_message', {'status': "ok", 'message': openning_sentence[0]})
    emit('receive_message', {'status': "ok", 'message': openning_sentence[1]})


@socketio.on('artquest2_request', namespace='/artquest2')
def artquest2_request(request):
    data = json.loads(request['data'])

    try:
        title = data['picture']["title"]
        author = data['picture']["author"]
        psgf = data['picture']["psgf"]
        subsf = data['picture']["subsf"]
        vmessage = data["conversation_list"][-1]

        responses = model.getResponse(title, author, psgf, subsf, vmessage)

        emit('receive_message', {'status': "ok", 'message': responses[0]})
        emit('receive_message', {'status': "ok", 'message': responses[1]})
    except Exception as e:
        print(e)
        status = 'Error occurred (See details in the log of backend application)'
        emit('receive_message', {'status': "failed", 'message': "Error"})