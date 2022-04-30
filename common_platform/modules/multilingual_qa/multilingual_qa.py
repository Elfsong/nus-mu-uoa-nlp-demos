from flask import Blueprint, render_template

multilingual_qa = Blueprint('multilingual_qa', __name__, template_folder='./templates', static_folder='./static')

@multilingual_qa.route('/')
def index():
    return render_template('multilingual_qa/index.html')