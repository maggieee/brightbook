from jinja2 import StrictUndefined
from flask import (Flask, render_template, flash, redirect, url_for, request, 
    session)
from flask_debugtoolbar import DebugToolbarExtension


import models
from models import connect_to_db

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


@app.route('/register')
def show_registration_page():
    """Show the register page"""

    return render_template("register.html")


@app.route('/register', methods=["POST"])

def register_user():
     """Register a new user with email and password."""

    email = request.form.get('email').strip()
    display_name = request.form.get('password').strip()
    password = request.form.get('password').strip()

    new_user = User(email=email, display_name=display_name)

    new_user.set_password(password)

    if len(User.query.filter_by(email=email).all()) == 0:

        db.session.add(new_user)
        db.session.commit()

        return redirect("/")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    connect_to_db(app)

     # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0", debug=True)