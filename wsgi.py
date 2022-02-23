#!/usr/bin/env python

"""
Application Entry Point
that imports and starts our entire app
"""

# init_app Initializes the core application
from flaskr.__init__ import init_app

app = init_app()

if __name__ == "__main__":
    # app.run(debug=True) # used for debugging
    app.run()
