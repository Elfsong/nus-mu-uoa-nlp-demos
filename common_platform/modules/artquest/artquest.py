from flask import Blueprint, render_template

artquest = Blueprint('artquest', __name__, template_folder='./templates', static_folder='./static')

@artquest.route('/')
def index():
    return render_template('artquest/index.html')