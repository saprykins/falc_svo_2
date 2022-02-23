#!/usr/bin/env python

"""
Initialization of Flask application Factory
"""

from flask import Flask

# import routes
from flaskr.controller import (
    get_file_info_blueprint,
    get_text_blueprint,
    index_blueprint,
    upload_file_blueprint,
)


def init_app(test_config=None):
    """
    Initialize the /core/ application
    """

    # Create a Flask app object
    app = Flask(__name__)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # Register Blueprints
    app.register_blueprint(index_blueprint)
    app.register_blueprint(upload_file_blueprint)
    app.register_blueprint(get_file_info_blueprint)
    app.register_blueprint(get_text_blueprint)

    return app
