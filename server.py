from jinja2 import StrictUndefined
from flask import (Flask, render_template, flash, redirect, url_for, request,
                   session)
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, CreateMessageForm, CreatePostForm
from sqlalchemy import text
import bleach
from datetime import datetime

import models
from models import User, Post, Heart, Message, db, connect_to_db

from helpers import (add_and_commit_thing_to_database, create_new_post_from_summernote,
                     get_current_user_from_session, delete_db_object)


app = Flask(__name__)
# session(app)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Show the homepage"""

    if 'email' in session:
        print("****SESSION****")
        print(session)

        email = session['email']
        user = User.query.filter_by(email=email).first_or_404()

        # print("****USER****")
        # print(user)

        return render_template("logged_in_homepage.html", user=user)

    else:
        return render_template("index.html")


@app.route('/brightbookers')
def show_brightbookers():
    """List the brightbookers"""

    return redirect('/users')


@app.route('/brightnews')
def show_brightnews():
    """Show the newsfeed"""

    posts = Post.query.order_by(text("posted_at desc"))

    hearts = Heart.query.all()

    users = User.query.all()

    if 'email' in session:

        return render_template("brightnews.html", posts=posts, hearts=hearts, users=users)

    else:
        flash('Please log in to see the BrightNews feed.')

        return redirect('/')


@app.route('/create_message/<user_id>')
def show_create_message_page(user_id):
    """Show the message page"""

    form = CreateMessageForm()

    return render_template("create_message.html", form=form, recipient=user_id)


@app.route('/create_message', methods=["POST"])
def create_message():
    """Create a new message with a sender, recipient, subject, and contents."""

    sender = get_current_user_from_session()
    recipient = request.form.get('recipient')

    new_message = Message(sender=sender.user_id, recipient=recipient, subject=request.form.get('subject'),
                          contents=request.form.get('editordata'))

    add_and_commit_thing_to_database(new_message)

    flash(f"Message sent to User {recipient}!")

    return redirect(f"/users/{recipient}")



@app.route('/create_post')
def show_create_post_page():
    """Show the register page"""

    form = CreatePostForm()

    return render_template("create_post.html", form=form)


@app.route('/create_post', methods=["POST"])
def create_post():
    """Create a new post with a user and post text."""

    user = get_current_user_from_session()
    new_post = create_new_post_from_summernote(user)
    add_and_commit_thing_to_database(new_post)

    return render_template("post_details.html", post=new_post, user=user)


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

        else:
            flash('Invalid login. Please try again.')

            return redirect('/login')


@app.route("/logout", methods=['GET', 'POST'])
def log_out_user():
    """Log the user out and remove them from the session."""

    print(session)

    session.clear()
    print(session)

    flash('Logout successful')

    return redirect("/")


@app.route("/messages")
def view_messages():
    """Show the current user's messages."""

    user = get_current_user_from_session()
    messages = Message.query.filter_by(recipient=user.user_id).order_by(text("sent_at desc"))

    return render_template("my_messages.html", user=user, messages=messages)


@app.route("/messages/<message_id>")
def show_message_details(message_id):
    """Show message details."""

    message = Message.query.filter_by(message_id=message_id).first_or_404()

    return render_template("message_details.html", message=message)

@app.route("/messages/<int:message_id>/delete", methods=["GET", "DELETE"])
def delete_message(message_id):

    message = Message.query.filter_by(message_id=message_id).first_or_404()

    delete_db_object(message)

    flash(f"Message {message.message_id} successfully deleted.")

    return redirect("/messages")

@app.route("/posts")
def redirect_from_posts_to_brightnews():
    """Redirect the user to BrightNews"""

    return redirect("brightnews")


@app.route("/posts/logout", methods=["GET", "POST"])
def redirect_from_posts_to_logout():
    """Redirect the user to the logout flow."""

    return redirect("/logout")


@app.route("/posts/<post_id>")
def show_post_details(post_id):
    """Show post details."""

    post = Post.query.filter_by(post_id=post_id).first_or_404()

    user_id = post.user_id

    user = User.query.filter_by(user_id=user_id).first_or_404()

    email = session['email']
    current_user = User.query.filter_by(email=email).first_or_404()

    return render_template("post_details.html", post=post, user=user,
                           current_user=current_user)


@app.route("/posts/<int:post_id>/delete", methods=["GET", "DELETE"])
def delete_post(post_id):

    post = Post.query.filter_by(post_id=post_id).first_or_404()

    if post.hearts:
        for heart in post.hearts:
            delete_db_object(heart)

    delete_db_object(post)

    flash(f"Post {post.post_id} successfully deleted.")

    return redirect('/')


@app.route('/posts/<int:post_id>/heart', methods=["POST"])
def add_heart(post_id):
    """Add a reaction to a post."""

    # print(post_id)

    print("***PATH***")
    print(request.path)

    post = Post.query.filter_by(post_id=post_id).first_or_404()
    user_id = post.user_id
    user = User.query.filter_by(user_id=post.user_id).first_or_404()

    email = session['email']
    current_user = User.query.filter_by(email=email).first_or_404()

    new_heart = Heart(
        post_id=post_id, user_id=current_user.user_id, heart_type=u"❤️")

    db.session.add(new_heart)
    db.session.commit()

    flash("Post <3'd")

    return redirect(f"/posts/{post_id}")


# @app.route("/profile/<user_id>")
# def show_my_profile(user_id):
#     """Show the logged-in user's profile."""

#     user = User.query.filter_by(email=session['email']).first_or_404()
#     user_id = user.user_id

#     return render_template("/user_details.html", user=user)


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

    if len(User.query.filter_by(email=email).all()) == 0  and len(User.query.filter_by(display_name=display_name).all()) == 0:

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful - please log in.")

        return redirect("/")

    else:

        flash("Email or display name has already been taken. Please try again.")

        return redirect("/")



@app.route("/user_details")
def show_user_details():
    """Show user details."""

    print(session)

    return render_template("user_details.html")


@app.route("/users")
def user_list():
    """Show list of users."""

    if 'email' in session:
        users = User.query.order_by("display_name")

        return render_template("brightbookers.html", users=users)

    else:
        flash('Please log in to view BrightBookers.')

        return redirect('/')


@app.route("/users/logout", methods=["GET", "POST"])
def redirect_to_logout():
    """Redirect the user to the logout flow."""

    return redirect("/logout")


@app.route("/users/<user_id>")
def show_user_id_details(user_id):
    """Show user details."""

    user = User.query.filter_by(user_id=user_id).first_or_404()

    return render_template("user_details.html", user=user)


@app.template_filter()
def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)


def humanize_ts(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(round(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(round(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"

app.jinja_env.filters['humanize'] = humanize_ts

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0", debug=True)
