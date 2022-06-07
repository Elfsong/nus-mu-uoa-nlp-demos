#!/bin/env python
import logging
from app import create_app, socketio

app = create_app(debug=True)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=3002)
    

"""
sudo /home/nzsg_nlp_nus/miniconda3/bin/gunicorn -k gevent \
                                                 -w 1 \
                                                 -b 0.0.0.0:443 \
                                                 -preload \
                                                 --access-logfile ./logs/access.log \
                                                 --error-logfile ./logs/error.log \
                                                 --log-level DEBUG \
                                                 --certfile /etc/letsencrypt/live/nlp-platform.online/fullchain.pem \
                                                 --keyfile /etc/letsencrypt/live/nlp-platform.online/privkey.pem \
                                                 -t 360 \
                                                 -D \
                                                 start:app

pstree -ap|grep gunicorn
"""