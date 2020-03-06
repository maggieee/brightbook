from jinja2 import StrictUndefined
from flask import (Flask, render_template, flash, redirect, url_for, request,
                   session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension
# from forms import (RegisterForm, LoginForm, CreateCompanyForm, CreateMessageForm, CreatePostForm, 
                    # CreateHiringPostForm)
from sqlalchemy import text
import bleach
from datetime import datetime

import models
from models import User, Post, Heart, HiringPost, Message, Company, db, connect_to_db

from helpers import (add_and_commit_thing_to_database, create_new_post_from_summernote,
                     create_new_hiring_post_from_summernote, get_current_user_from_session, delete_db_object)


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

        email = session['email']
        user = User.query.filter_by(email=email).first_or_404()

        companies = Company.query.order_by("company_name")

        posts = Post.query.order_by(text("posted_at desc"))

        hearts = Heart.query.all()

        users = User.query.all()

        return render_template("logged_in_homepage.html", companies = companies, user=user, 
        posts=posts, hearts=hearts, users=users)

    else:
        return render_template("index.html")


@app.route("/api/v1/companies")
def company_list_api():
    """Show JSON list of companies."""

    if 'email' in session:
        companies = Company.query.all()

        comps = {}

        for comp in companies:
            comps[comp.company_name] = {'company_id': comp.company_id,
                                            'hired_bootcamp_grads': comp.hired_bootcamp_grads,
                                            'hired_hackbrighters': comp.hired_hackbrighters,
                                            'job_listings_link': comp.job_listings_link,
                                            'company_contact': comp.company_contact,
                                            'joined_at': comp.joined_at}

        return jsonify(comps)

    else:
        flash('Please log in to view Companies.')

        return redirect('/')


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


@app.route("/companies")
def company_list():
    """Show list of companies."""

    if 'email' in session:
        companies = Company.query.order_by("company_name")

        return render_template("company_directory.html", companies=companies)

    else:
        flash('Please log in to view Companies.')

        return redirect('/')


@app.route("/companies/<company_id>")
def show_company_details(company_id):
    """Show company details."""

    company = Company.query.filter_by(company_id=company_id).first_or_404()

    return render_template("company_details.html", company=company)


@app.route("/company_search")
def company_search():
    """Return search results for a company."""

    company_name = request.args.get("company_name")

    print(company_name)

    company = Company.query.filter_by(company_name=company_name).first()

    print(company)

    # comp = {}

    comp = {'company_name': company.company_name,
            'company_id': company.company_id,
            'hired_bootcamp_grads': company.hired_bootcamp_grads,
            'hired_hackbrighters': company.hired_hackbrighters,
            'job_listings_link': company.job_listings_link,
            'company_contact': company.company_contact,
            'joined_at': company.joined_at}

    return jsonify(comp)


@app.route("/company_status")
def get_company_status():
    """Get company status."""

    company_name = request.args.get("company_name")

    if Company.query.filter_by(company_name=company_name).first() is not None:
        return f"{company_name} has been submitted and is under review."

    if Company.query.filter_by(company_name=company_name).first() is None:
        return f"{company_name} has either already been approved or is not yet submitted. Please check reviewed listings below and submit if it's not already there!"


@app.route('/create_company')
def show_create_company_page():
    """Show the add a company page"""

    # form = CreateCompanyForm()

    return render_template("create_company.html")


@app.route('/create_company', methods=["POST"])
def create_company():
    """Add a new company."""

    company_name = request.form.get('company_name').strip()
    hired_hackbrighters = True
    
    if request.form.get('hired_hackbrighters') == 'n':
        hired_hackbrighters = False

    hired_bootcamp_grads = True
    
    if request.form.get('hired_bootcamp_grads') == 'n':
        hired_hackbrighters = False

    job_listings_link = request.form.get('job_listings_link').strip()
    company_contact = request.form.get('company_contact').strip()
    company_notes = request.form.get('company_notes').strip()

    new_company = Company(company_name=company_name, hired_hackbrighters=hired_hackbrighters, 
        hired_bootcamp_grads=hired_bootcamp_grads, job_listings_link=job_listings_link, 
        company_contact=company_contact, company_notes=company_notes)

    if len(Company.query.filter_by(company_name=company_name).all()) == 0:

        add_and_commit_thing_to_database(new_company)

        flash("The company was successfully added!")

        return redirect("/companies")

    else:

        flash("Company name has already been taken. Please try again.")

        return redirect("/create_company")


@app.route('/create_message/<user_id>')
def show_create_message_page(user_id):
    """Show the message page"""

    # form = CreateMessageForm()

    return render_template("create_message.html", recipient=user_id)


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

@app.route('/create_hiring_post')
def show_create_hiring_post_page():
    """Show the hiring post page"""

    # form = CreateHiringPostForm()

    return render_template("create_hiring_post.html")


@app.route('/create_hiring_post', methods=["POST"])
def create_hiring_post():
    """Create a new hiring post with a user and post text."""

    user = get_current_user_from_session()
    new_post = create_new_hiring_post_from_summernote(user)
    add_and_commit_thing_to_database(new_post)

    return render_template("hiring_post_details.html", hiring_post=new_post, user=user)

@app.route('/create_post')
def show_create_post_page():
    """Show the register page"""

    # form = CreatePostForm()

    return render_template("create_post.html")


@app.route('/create_post', methods=["POST"])
def create_post():
    """Create a new post with a user and post text."""

    user = get_current_user_from_session()
    new_post = create_new_post_from_summernote(user)
    add_and_commit_thing_to_database(new_post)

    return render_template("post_details.html", post=new_post, user=user)


@app.route("/get_company_status")
def show_company_status():
    """Get and show a company's status."""

    return render_template("company_status.html")

@app.route('/hiring_posts')
def show_hiring_posts():
    """Show the hiring post feed"""

    hiring_posts = HiringPost.query.order_by(text("posted_at desc"))

    users = User.query.all()

    if 'email' in session:

        return render_template("hiring_posts.html", hiring_posts=hiring_posts, users=users)

    else:
        flash('Please log in to see the hiring feed.')

        return redirect('/')


@app.route('/login')
def show_login():
    """Show the login page/module"""

    # form = LoginForm()

    return render_template("login.html")


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

    # form = RegisterForm()
    # if form.validate_on_submit():
    #     return redirect(url_for('success'))

    return render_template("register.html")


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

    if session['email'] == user.email:
        return render_template("my_profile.html", user=user)

    return render_template("user_details.html", user=user)

### Jinja filters below ####

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

connect_to_db(app)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0", debug=True)
