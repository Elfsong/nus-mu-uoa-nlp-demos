from flask import Flask, redirect, url_for
from flask_socketio import SocketIO
import logging

socketio = SocketIO(async_mode="threading")

def create_app(debug=False):
    # Create an application
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

    # Combine Gunicorn logging and Flask logging
    gunicorn_error_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers.extend(gunicorn_error_logger.handlers)
    app.logger.setLevel(logging.DEBUG)

    # App route
    @app.route('/')
    def index():
        return redirect(url_for('homepage.index'))

    @app.route('/nzsg-nlp')
    def nzsg_rerouter():
        return redirect("https://nlp-platform.online:8443/nzsg-nlp/")
    
    # Service registering
    app.logger.info("Registering services...")
    
    from .homepage import homepage as homepage_blueprint
    app.register_blueprint(homepage_blueprint, url_prefix='/homepage')
    app.logger.info("[homepage_blueprint] registed!")

    from .artquest import artquest as artquest_blueprint
    app.register_blueprint(artquest_blueprint, url_prefix='/artquest')
    app.logger.info("[artquest_blueprint] registed!")

    from .multilingual_qa import multilingual_qa as multilingual_qa_blueprint
    app.register_blueprint(multilingual_qa_blueprint, url_prefix='/multilingual_qa')
    app.logger.info("[multilingual_qa_blueprint] registed!")

    from .line_bot import line_bot as line_bot_blueprint
    app.register_blueprint(line_bot_blueprint, url_prefix='/line_bot')
    app.logger.info("[line_bot_blueprint] registed!")

    from .cure import cure as cure_blueprint
    app.register_blueprint(cure_blueprint, url_prefix='/cure')
    app.logger.info("[cure_blueprint] registed!")

    # Init socketio
    socketio.init_app(app, async_mode='threading')

    app.logger.info("Ready to go!")
    return app