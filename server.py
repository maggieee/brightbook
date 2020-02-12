from jinja2 import StrictUndefined
from flask import (Flask, render_template, flash, redirect, url_for, request, session)
from flask_debugtoolbar import DebugToolbarExtension


import models

app = Flask(__name__)
#session(app)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    return 'Hi'


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    connect_to_db(app)

     # Use the DebugToolbar
    DebugToolbarExtension(app)
    
    app.run(host="0.0.0.0", debug=True)