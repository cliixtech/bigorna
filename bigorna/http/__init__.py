import logging

from flask import Flask

from .rest import api


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

app = Flask('Bigorna')
app.register_blueprint(api, url_prefix='/api')


@app.route('/ping')
def heartbeat():
        return '<html><body style="font-family:courier new;">pong!</body></html>'
