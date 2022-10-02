from flask import Flask, redirect, url_for, jsonify
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

    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return jsonify({"Status": "Unloaded", "Solution": "Ask admin to load the application."}), 404
    
    # Service registering
    app.logger.info("Registering services...")
    # app.register_error_handler(404, page_not_found)
    
    from .homepage import homepage as homepage_blueprint
    app.register_blueprint(homepage_blueprint, url_prefix='/homepage')
    app.logger.info("[homepage_blueprint] registed!")

    # from .socratic_qg import socratic_qg as socratic_qg_blueprint
    # app.register_blueprint(socratic_qg_blueprint, url_prefix='/socratic_qg')
    # app.logger.info("[socratic_qg_blueprint] registed!")

    # from .artquest import artquest as artquest_blueprint
    # app.register_blueprint(artquest_blueprint, url_prefix='/artquest')
    # app.logger.info("[artquest_blueprint] registed!")

    # from .artquest2 import artquest2 as artquest2_blueprint
    # app.register_blueprint(artquest2_blueprint, url_prefix='/artquest2')
    # app.logger.info("[artquest2_blueprint] registed!")

    # from .artmuse import artmuse as artmuse_blueprint
    # app.register_blueprint(artmuse_blueprint, url_prefix='/artmuse')
    # app.logger.info("[artmuse_blueprint] registed!")

    # from .multilingual_qa import multilingual_qa as multilingual_qa_blueprint
    # app.register_blueprint(multilingual_qa_blueprint, url_prefix='/multilingual_qa')
    # app.logger.info("[multilingual_qa_blueprint] registed!")

    from .line_bot import line_bot as line_bot_blueprint
    app.register_blueprint(line_bot_blueprint, url_prefix='/line_bot')
    app.logger.info("[line_bot_blueprint] registed!")

    from .whatsapp_bot import whatsapp_bot as whatsapp_bot_blueprint
    app.register_blueprint(whatsapp_bot_blueprint, url_prefix='/whatsapp_bot')
    app.logger.info("[whatsapp_bot_blueprint] registed!")

    # from .cure import cure as cure_blueprint
    # app.register_blueprint(cure_blueprint, url_prefix='/cure')
    # app.logger.info("[cure_blueprint] registed!")

    # Init socketio
    socketio.init_app(app, async_mode='threading')

    app.logger.info("Ready to go!")
    return app