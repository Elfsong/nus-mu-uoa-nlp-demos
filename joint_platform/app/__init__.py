from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()

def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

    from .homepage import homepage as homepage_blueprint
    app.register_blueprint(homepage_blueprint, url_prefix='/homepage')

    from .artquest import artquest as artquest_blueprint
    app.register_blueprint(artquest_blueprint, url_prefix='/artquest')

    from .multilingual_qa import multilingual_qa as multilingual_qa_blueprint
    app.register_blueprint(multilingual_qa_blueprint, url_prefix='/multilingual_qa')

    from .line_bot import line_bot as line_bot_blueprint
    app.register_blueprint(line_bot_blueprint, url_prefix='/line_bot')

    socketio.init_app(app)
    return app