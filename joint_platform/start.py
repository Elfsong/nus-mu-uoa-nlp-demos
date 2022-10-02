#!/bin/env python
import logging
from app import create_app, socketio

app = create_app(debug=False)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=443)