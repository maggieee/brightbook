from jinja2 import StrictUndefined
from flask import (Flask, render_template, flash, redirect, url_for, request, 
    session)
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm


import models
from models import User, db, connect_to_db

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


@app.route('/login')
def show_login():
    """Show the login page/module"""

    form = LoginForm()

    return render_template("login.html", form=form)


@app.route('/login', methods=['POST'])
def log_in_user():
    """Log the user in if they have valid credentials."""

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')


        user = User.query.filter_by(email=email).all()

        if len(user) != 0:
            if user[0].check_password(password) == True:
                session['email'] = user[0].email
                session['password'] = user[0].password_hash
                flash('You were successfully logged in')
                print(session)

                return redirect('/')

            else:
                flash('Password incorrect')

                return redirect('/login')


@app.route('/register')
def show_registration_page():
    """Show the register page"""

    form = RegisterForm()
    # if form.validate_on_submit():
    #     return redirect(url_for('success'))

    return render_template("register.html", form=form)


@app.route('/register', methods=["POST"])

def register_user():
    """Register a new user with email, display name, and password."""

    email = request.form.get('email').strip()
    display_name = request.form.get('display_name').strip()
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