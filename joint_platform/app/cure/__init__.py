# coding: utf-8

# Author: Mingzhe Du
# Date: 2022-07-08
# Email: mingzhe@nus.edu.sg

from flask import Blueprint, render_template, request
from flask import current_app
from flask_socketio import emit
from .. import socketio

from datetime import datetime
from . stream_reader import StreamReader
from . tweets_preprocessor import TweetProcessor
from . clustering_processor import TweetsCluster
from . clustering_render import ClusterRender
from . classifier import TweetClassifier

cure = Blueprint('cure', __name__, template_folder='./templates', static_folder='./static')

date = datetime.today()
data_string = "%i-%02d-%02d" % (date.year, date.month, date.day)

async_sessions = dict()

def step_1_callback(data, socketio, client_id):
    socketio.emit('update_tweets', {"tweet": data["text"], "date": data["created_at"]}, broadcast=False, namespace="/cure", to=client_id)


def step_4_callback(result, tweet, socketio, client_id):
    instance = {
        "icon": "<span class='mif-plus fg-green'>" if result == "True" else "<span class='mif-minus fg-red'>", 
        "caption": tweet
    }
    socketio.emit('update_status', {"step": 4, "task": "pipeline", "status": "pulse", "data": instance}, broadcast=False, namespace="/cure", to=client_id)

# Global Object since it is too big
tcc = TweetClassifier(step_4_callback)

def step_1_processor(client_id, data):
    task = data["task"]
    if task == "search":
        sr = StreamReader("test", socketio, client_id, step_1_callback)
        async_sessions[client_id] = sr
        keywords = data["keywords"]
        kwlist = keywords.split(",")
        sr.filter(kwlist)
    elif task == "stop":
        async_sessions[client_id].stop()
        print("Search Stopped")

def step_2_processor(client_id, data):
    if data["task"] == "pipeline":
        tp = TweetProcessor()
        tp.preprocess("test", data_string)
        tp.convert("test", data_string)
        emit('update_status', {"step": 2, "task": "pipeline", "status": "done"}, broadcast=False, namespace="/cure", room=client_id)
    else:
        print("unknown task")

def step_3_processor(client_id, data):
    if data["task"] == "pipeline":
        tc = TweetsCluster()
        tc.cluster("test", data_string)
        tc.filter("test", data_string)

        cr = ClusterRender()
        datasets = list()
        cr.render_js("test", data_string, datasets)

        emit('update_status', {"step": 3, "task": "pipeline", "status": "done", "data": datasets}, broadcast=False, namespace="/cure", room=client_id)
    else:
        print("unknown task")

def step_4_processor(client_id, data):
    if data["task"] == "pipeline":
        tcc.process("test", data_string, socketio, client_id)

        emit('update_status', {"step": 4, "task": "pipeline", "status": "done"}, broadcast=False, namespace="/cure", room=client_id)
    else:
        print("unknown task")

@cure.route('/')
def index():
    return render_template('cure/index.html')

@socketio.on('connect', namespace='/cure')
def on_connect():
    client_id = request.sid
    print(f'new connection,id: {client_id}')

@socketio.on('coordinator', namespace='/cure')
def coordinate(data):
    step = data["step"]

    if step == 1:
        step_1_processor(request.sid, data)
    elif step == 2:
        step_2_processor(request.sid, data)
    elif step == 3:
        step_3_processor(request.sid, data)
    elif step == 4:
        step_4_processor(request.sid, data)

    print("Coordinate Function Call Finished")

