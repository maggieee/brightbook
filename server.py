from jinja2 import StrictUndefined
from flask import (Flask, render_template, flash, redirect, url_for, request, 
    session)
from flask_debugtoolbar import DebugToolbarExtension
from forms import RegisterForm, LoginForm, CreatePostForm


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

    posts = Post.query.all()

    hearts = Heart.query.all()

    users = User.query.all()

    if 'email' in session:

        return render_template("brightnews.html", posts=posts, hearts=hearts, users=users)

    else:
        flash('Please log in to see the BrightNews feed.')

        return redirect('/')

@app.route('/create_post')
def show_create_post_page():
    """Show the register page"""

    form = CreatePostForm()
    # if form.validate_on_submit():
    #     return redirect(url_for('success'))

    return render_template("create_post.html", form=form)

@app.route('/create_post', methods=["POST"])
def create_post():
    """Create a new post with a user and post text."""

    email = session['email']
    user = User.query.filter_by(email=email).first_or_404()

    post_text = request.form.get('post_text').strip()

    new_post = Post(user_id=user.user_id, post_text=post_text)

    db.session.add(new_post)
    db.session.commit()

    email = session['email']
    current_user = User.query.filter_by(email=email).first_or_404()

    return render_template("post_details.html", post=new_post, user=user,
        current_user=current_user)


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

    new_heart = Heart(post_id=post_id, user_id=current_user.user_id, heart_type="red_heart")

    db.session.add(new_heart)
    db.session.commit()


    flash("Post <3'd")

    return redirect(f"/posts/{post_id}")

@app.route("/profile/<user_id>")
def show_my_profile(user_id):
    """Show the logged-in user's profile."""

    user = User.query.filter_by(email=session['email']).first_or_404()
    user_id = user.user_id

    return render_template("/user_details.html", user=user)


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

    if 'email' in session:
        users = User.query.all()

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



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    connect_to_db(app)

     # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0", debug=True)