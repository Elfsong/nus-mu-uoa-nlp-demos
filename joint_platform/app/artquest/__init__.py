from flask import Blueprint, render_template, Response
from flask_socketio import emit
from . model import ArtQuestModel
from .. import socketio
import json

artquest = Blueprint('artquest', __name__, template_folder='./templates', static_folder='./static')
artquest_model = ArtQuestModel("Elfsong/ArtQuest")

def get_file(filename):
    try:
        return open(filename).read()
    except IOError as exc:
        return str(exc)

@artquest.route('/')
def index():
    return render_template('artquest/index.html')

@artquest.route('/demo')
def demo():
    content = get_file("modules/artquest/templates/artquest/demo.html")
    return Response(content, mimetype="text/html")

@socketio.on('artquest_request', namespace='/artquest')
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