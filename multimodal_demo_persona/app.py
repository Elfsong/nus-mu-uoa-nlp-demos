# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#
#   Organisation: Broad AI Lab, University of Auckland
#   Author: Ziqi Wang
#   Date: 2021-05-11
#
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# from sys import path
# path.append("../")
# path.reverse()

import os
import sys
import time
import json

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from nltk import tokenize

from model import Broker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

# broker
broker = Broker("./static/data/persona")

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
def index():
    return render_template('index.html')

@socketio.on('predict')
def predict_request(request):
    data = json.loads(request['data'])
    print("Received data:", data)

    result = {}
    status = "init"

    try:
        result["response"] = broker.question_generation(data["persona"], data["conversation_list"])
        status = "completed"

        emit('update_status', {'status': status, 'result': result})
    except Exception as e:
        print(e)
        status = 'Error occurred (See details in the log of backend application)'
        emit('update_status', {'status': status, 'result': result})

# Main loop
if __name__ == "__main__":
    port_num = 3000
    while port_num < 0 or port_num > 65535 or is_port_occupied(port_num):
        port_num = int_with_default(input('Please specify a port number (0 - 65535): '), -1)

    socketio.run(app, host="0.0.0.0", port=port_num)
