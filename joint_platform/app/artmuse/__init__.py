from flask import Blueprint, render_template, Response
from flask_socketio import emit
from .. import socketio
import json

import app.artmuse.model as model

artmuse = Blueprint('artmuse', __name__, template_folder='./templates', static_folder='./static')

@artmuse.route('/')
def index():
    return render_template('artmuse/index.html')

@socketio.on('get_openning', namespace='/artmuse')
def get_openning(request):
    data = json.loads(request['data'])

    title = data['picture']["title"]
    author = data['picture']["author"]

    openning_sentences = model.get_openning_sentence(title, author)

    emit('receive_message', {'status': "ok", 'message': openning_sentences[0]})
    emit('receive_message', {'status': "ok", 'message': openning_sentences[1]})


@socketio.on('artmuse_request', namespace='/artmuse')
def artmuse_request(request):
    data = json.loads(request['data'])

    try:
        title = data['picture']["title"]
        author = data['picture']["author"]
        psgf = data['picture']["psgf"]
        subsf = data['picture']["subsf"]
        seen = data["seen"]
        seen_questions = data["seen_questions"]
        vmessage = data["conversation_list"][-1]

        responses = model.getResponse(title, author, psgf, subsf, seen, seen_questions, vmessage)

        print("Responses:", responses)

        emit('receive_message', {'status': "ok", 'message': responses[0]})
        emit('receive_message', {'status': "ok", 'message': responses[1]})
        emit('receive_seen', {'status': "ok", 'seen': responses[2], 'seen_questions': responses[3]})
    except Exception as e:
        print(e)
        status = 'Error occurred (See details in the log of backend application)'
        emit('receive_message', {'status': "failed", 'message': "Error"})