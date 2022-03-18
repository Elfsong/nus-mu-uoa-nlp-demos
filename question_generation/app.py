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
broker = Broker()

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
    completed = 0
    total_step = 4

    try:
        status = '0/3 - Converting data for prediction model...'
        emit('update_status', {'status': status, 'cur_step': 0, 'total_step': total_step, 'completed': completed, 'result': result})
        time.sleep(2)

        status = '1/3 - Do something 1...'
        emit('update_status', {'status': status, 'cur_step': 1, 'total_step': total_step, 'completed': completed, 'result': result})
        time.sleep(2)

        status = '2/3 - Do something 2...'
        emit('update_status', {'status': status, 'cur_step': 2, 'total_step': total_step, 'completed': completed, 'result': result})
        time.sleep(2)

        status = '3/3 - Do something 3...'
        emit('update_status', {'status': status, 'cur_step': 3, 'total_step': total_step, 'completed': completed, 'result': result})
        time.sleep(2)

        completed = 1
        status = 'Done!'
        result = {
            "best_question": "It's a fake inference lah!", 
            "questions": ["other question 1", "other question 2", "other question 3"]
        }
        emit('update_status', {'status': status, 'cur_step': 4, 'total_step': total_step, 'completed': completed, 'result': result})
    except Exception as e:
        print(e)
        status = 'Error occurred'
        emit('update_status', {'status': status, 'cur_step': -1, 'total_step': total_step, 'completed': 1, 'result': result})

# Main loop
if __name__ == "__main__":
    port_num = 3000
    while port_num < 0 or port_num > 65535 or is_port_occupied(port_num):
        port_num = int_with_default(input('Please specify a port number (0 - 65535): '), -1)

    socketio.run(app, host="0.0.0.0", port=port_num)
