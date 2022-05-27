from flask import Blueprint, render_template
from flask_socketio import emit
from .. import socketio
from . model import MultilingualQAModel
import json
import time

multilingual_qa = Blueprint('multilingual_qa', __name__, template_folder='./templates', static_folder='./static')

multilingual_qa_model = MultilingualQAModel()

@multilingual_qa.route('/')
def index():
    return render_template('multilingual_qa/index.html')


@socketio.on('multilingual_qa_request', namespace='/multilingual_qa')
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
