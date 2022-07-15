#!/bin/env python
import logging
from app import create_app, socketio

app = create_app(debug=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=443)
    

"""
    sudo env OPENAI_API_KEY=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 \
    /home/nzsg_nlp_nus/miniconda3/bin/gunicorn  -w 1 \
                                                -b 0.0.0.0:443 \
                                                -preload \
                                                --access-logfile ./logs/access.log \
                                                --error-logfile ./logs/error.log \
                                                --log-level DEBUG \
                                                --certfile /etc/letsencrypt/live/nlp-platform.online/fullchain.pem \
                                                --keyfile /etc/letsencrypt/live/nlp-platform.online/privkey.pem \
                                                -t 360 \
                                                -k gevent \
                                                -D \
                                                start:app

    pstree -ap|grep gunicorn
"""