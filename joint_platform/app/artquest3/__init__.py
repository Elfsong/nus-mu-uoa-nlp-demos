from flask import Blueprint, render_template, Response
from flask_socketio import emit
from .. import socketio
import json

import app.artquest3.model as model

artquest3 = Blueprint('artquest3', __name__, template_folder='./templates', static_folder='./static')

@artquest3.route('/')
def index():
    return render_template('artquest3/index.html')

@socketio.on('get_openning', namespace='/artquest3')
def get_openning(request):
    data = json.loads(request['data'])

    title = data['picture']["title"]
    author = data['picture']["author"]

    openning_sentence = model.get_openning_sentence(title, author)

    emit('receive_message', {'status': "ok", 'message': openning_sentence[0]})
    emit('receive_message', {'status': "ok", 'message': openning_sentence[1]})


@socketio.on('artquest3_request', namespace='/artquest3')
def artquest3_request(request):
    data = json.loads(request['data'])

    try:
        title = data['picture']["title"]
        author = data['picture']["author"]
        psgf = data['picture']["psgf"]
        subsf = data['picture']["subsf"]
        seen = data["seen"]
        seen_questions = data["seen_questions"]
        vmessage = data["conversation_list"][-1]

        print(data)

        responses = model.getResponse(title, author, psgf, subsf, seen, seen_questions, vmessage)

        print("Responses:", responses)

        emit('receive_message', {'status': "ok", 'message': responses[0]})
        emit('receive_message', {'status': "ok", 'message': responses[1]})
        emit('receive_seen', {'status': "ok", 'seen': responses[2], 'seen_questions': responses[3]})
    except Exception as e:
        print(e)
        status = 'Error occurred (See details in the log of backend application)'
        emit('receive_message', {'status': "failed", 'message': "Error"})