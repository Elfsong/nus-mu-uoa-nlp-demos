# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#
#   Organisation: Broad AI Lab, University of Auckland
#   Author: Ziqi Wang
#   Date: 2021-05-11
#
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# from sys import path
# path.append("./")
# path.reverse()

import os
import sys
import time
import json

from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit

from modules.homepage.homepage import homepage

from modules.artquest.artquest import artquest
from modules.artquest.model import ArtQuestModel

from modules.multilingual_qa.multilingual_qa import multilingual_qa
from modules.multilingual_qa.model import MultilingualQAModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')


def int_with_default(input, default=0):
    try:
        i = int(input)
    except ValueError:
        i = default
    return i

def is_port_occupied(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(('localhost', port))
        if result == 0:
            print('**WARNING MESSAGE: port ' + str(port) + ' is in use.')
        return result == 0

@app.route('/')
def hello_world():
    return 'Hello, World!'

# homepage
app.register_blueprint(homepage, url_prefix='/homepage')

# artquest
app.register_blueprint(artquest, url_prefix='/artquest')
artquest_model = ArtQuestModel("./modules/artquest/static/data/persona")

@socketio.on('artquest_request')
def artquest_request(request):
    data = json.loads(request['data'])
    result = {}

    try:
        result["response"] = artquest_model.question_generation(data["persona"], data["conversation_list"])
        status = "completed"
        emit('update_status', {'status': status, 'result': result})
    except Exception as e:
        print(e)
        status = 'Error occurred (See details in the log of backend application)'
        emit('update_status', {'status': status, 'result': result})

# multilingual_qa
app.register_blueprint(multilingual_qa, url_prefix='/multilingual_qa')
multilingual_qa_model = MultilingualQAModel()

@socketio.on('multilingual_qa_request')
def multilingual_qa_request(request):
    data = json.loads(request['data'])
    question = data['question']
    context = data['context']
    language = data['language']
    result = {}
    completed = 0
    total_step = 4

    try:
        status = '0/3 - Converting data for prediction model...'
        emit('update_status', {'status': status, 'cur_step': 0, 'total_step': total_step, 'completed': completed, 'result': result})
        time.sleep(2)

        status = '1/3 - Document retrieval...'
        emit('update_status', {'status': status, 'cur_step': 1, 'total_step': total_step, 'completed': completed, 'result': result})
        multilingual_qa_model.document_retrieval(language, context, question, result)
        time.sleep(2)

        status = '2/3 - Paragraph retrieval...'
        emit('update_status', {'status': status, 'cur_step': 2, 'total_step': total_step, 'completed': completed, 'result': result})
        multilingual_qa_model.passage_retrieval(language, context, question, result)
        time.sleep(2)

        status = '3/3 - Question Answering...'
        emit('update_status', {'status': status, 'cur_step': 3, 'total_step': total_step, 'completed': completed, 'result': result})
        multilingual_qa_model.question_answering(language, context, question, result)
        time.sleep(2)

        completed = 1
        status = 'Done!'
        emit('update_status', {'status': status, 'cur_step': 4, 'total_step': total_step, 'completed': completed, 'result': result})
    except Exception as e:
        print(e)
        status = 'Error occurred'
        emit('update_status', {'status': status, 'cur_step': -1, 'total_step': total_step, 'completed': 1, 'result': result})

# Main loop
if __name__ == "__main__":
    port_num = 443
    while port_num < 0 or port_num > 65535 or is_port_occupied(port_num):
        port_num = int_with_default(input('Please specify a port number (0 - 65535): '), -1)

    socketio.run(app, host="0.0.0.0", ssl_context=('/etc/letsencrypt/live/nlp-platform.online-0001/fullchain.pem', '/etc/letsencrypt/live/nlp-platform.online-0001/privkey.pem'))