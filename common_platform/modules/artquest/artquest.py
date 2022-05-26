from flask import Blueprint, render_template, Response

artquest = Blueprint('artquest', __name__, template_folder='./templates', static_folder='./static')

def get_file(filename):  # pragma: no cover
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