from flask import Blueprint, render_template, Response
from flask_socketio import emit
from .. import socketio
import json

artquest2 = Blueprint('artquest2', __name__, template_folder='./templates', static_folder='./static')

@artquest2.route('/')
def index():
    return render_template('artquest2/index.html')


# @socketio.on('artquest_request', namespace='/artquest')
# def artquest_request(request):
#     data = json.loads(request['data'])
#     result = {}

#     try:
#         result["response"] = artquest_model.question_generation(data["persona"], data["conversation_list"])
#         status = "completed"
#         emit('update_status', {'status': status, 'result': result})
#     except Exception as e:
#         print(e)
#         status = 'Error occurred (See details in the log of backend application)'
#         emit('update_status', {'status': status, 'result': result})