from flask import Blueprint, render_template

homepage = Blueprint('homepage', __name__, template_folder='./templates', static_folder='./static')

@homepage.route('/')
def index():
    return render_template('homepage/index.html')