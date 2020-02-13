from jinja2 import StrictUndefined
from flask import (Flask, render_template, flash, redirect, url_for, request, 
    session)
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm


import models
from models import User, Post, Heart, db, connect_to_db

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
    """Show the homepage"""

    return render_template("index.html")

@app.route('/brightbookers')
def show_brightbookers():
    """List the brightbookers"""

    return redirect('/users')


@app.route('/brightnews')
def show_brightnews():
    """Show the newsfeed"""

    posts = Post.query.all()

    hearts = Heart.query.all()

    users = User.query.all()

    if 'email' in session:

        return render_template("brightnews.html", posts=posts, hearts=hearts, users=users)

    else:
        flash('Please log in to see the BrightNews feed.')

        return redirect('/')

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


@app.route("/logout", methods=['POST'])
def log_out_user():
    """Log the user out and remove them from the session."""

    print(session)

    session.clear()
    print(session)

    flash('Logout successful')

    return redirect("/")


@app.route("/profile")
def show_my_profile(user_id):
    """Show the logged-in user's profile."""


    user = User.query.filter_by(email=session['email']).first_or_404()
    user_id = user.user_id

    render_template("/users/<user_id>")


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


@app.route("/user_details")
def show_user_details():
    """Show user details."""

    print(session)

    return render_template("user_details.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("brightbookers.html", users=users)


@app.route("/users/<user_id>")
def show_user_id_details(user_id):
    """Show user details."""

    user = User.query.filter_by(user_id=user_id).first_or_404()


    return render_template("user_details.html", user=user)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    connect_to_db(app)

     # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0", debug=True)