import datetime
import hashlib
import os

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash



db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Data model for a user."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    display_name = db.Column(db.String(64), nullable=False, unique=True)
    profile_photo = db.Column(db.String(100), nullable=True)
    about_me = db.Column(db.Text, nullable=True)
    joined_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.datetime.now)
    user_type = db.Column(db.String(64), nullable=False, default=False)

    posts = db.relationship('Post')
    hearts = db.relationship('Heart')
    messages = db.relationship('Message')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.user_id} name={self.display_name}>"

    def avatar(self, size):
        """Get an avatar for the user from Gravatar"""
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (hashlib.md5(self.email.encode('utf-8')).hexdigest(), size)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Code to revist if adding un-heart capabilities

    # def heart_post(self, post, heart_type):
    #     if not self.has_hearted_post(post):
    #         heart = Heart(user_id=self.id, post_id=post.id, heart_type=heart_type)
    #         db.session.add(heart)
    #         db.session.commit()

    # def unheart_post(self, post):
    #     if self.has_hearted_post(post):
    #         Heart.query.filter_by(user_id=self.id, post_id=post.id).delete()

    # def has_hearted_post(self, post):
    #     return Heart.query.filter(
    #         Heart.user_id == self.id,
    #         Heart.post_id == post.id).count() > 0


class Post(db.Model):
    """Data model for a post."""

    __tablename__ = "posts"

    post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.user_id'), nullable=False)
    posted_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.datetime.now)
    post_text = db.Column(db.Text, nullable=False)

    users = db.relationship('User')
    hearts = db.relationship('Heart')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Post post_id={self.post_id} text={self.post_text[:30]}>"


class Heart(db.Model):
    """Data model for a post."""

    __tablename__ = "hearts"

    heart_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.user_id'), nullable=False)
    heart_type = db.Column(db.String(50), nullable=False)
    hearted_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.now)

    posts = db.relationship('Post')
    users = db.relationship('User')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Heart post_id={self.post_id} user_id={self.user_id} type={self.heart_type}>"


class Message(db.Model):
    """Data model for a message."""

    __tablename__ = "messages"

    message_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    sender = db.Column(db.Integer, db.ForeignKey(
        'users.user_id'), nullable=False)
    recipient = db.Column(db.Integer, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=False,
                        default=datetime.datetime.now)
    subject = db.Column(db.String(100), nullable=False)
    contents = db.Column(db.Text, nullable=False)

    senders = db.relationship('User')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Msg message_id={self.message_id} sender={self.sender} recipient={self.recipient}>"


class HiringPost(db.Model):
    """Data model for a post."""

    __tablename__ = "hiring_posts"

    hiring_post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.user_id'), nullable=False)
    posted_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.datetime.now)
    post_text = db.Column(db.Text, nullable=False)

    users = db.relationship('User')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<HiringPost hiring_post_id={self.hiring_post_id} text={self.post_text[:30]}>"


class Company(db.Model):
    """Data model for a company."""

    __tablename__ = "companies"

    company_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False, unique=True)
    hired_bootcamp_grads = db.Column(db.Boolean, nullable=False)
    hired_hackbrighters = db.Column(db.Boolean, nullable=False)
    job_listings_link = db.Column(db.String(300), nullable=True)
    company_contact = db.Column(db.String(300), nullable=True)
    company_notes = db.Column(db.Text, nullable=True)
    joined_at = db.Column(db.DateTime, nullable=False,
                          default=datetime.datetime.now)

##############################################################################
# Helper functions


def connect_to_db(app, db_uri=os.getenv('DATABASE_URL')):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
