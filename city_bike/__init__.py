#!/usr/bin/env python3

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.config.from_object(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

import city_bike.views

if __name__ == '__main__':
    app.run()
