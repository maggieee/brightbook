import datetime

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
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    posts = db.relationship('Post')
    hearts = db.relationship('Heart')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<User user_id={self.user_id} name={self.display_name}>"


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    """Data model for a post."""

    __tablename__ = "posts"

    post_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    posted_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    post_text = db.Column(db.String(1000), nullable=False)

    users = db.relationship('User')
    hearts = db.relationship('Heart')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Post post_id={self.post_id} text={self.post_text[:30]}>"


class Heart(db.Model):
    """Data model for a post."""

    __tablename__ = "hearts"

    heart_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    heart_type = db.Column(db.String(50), nullable=False)
    hearted_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

    posts = db.relationship('Post')
    users = db.relationship('User')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return f"<Heart post_id={self.post_id} user_id={self.user_id} type={self.heart_type}>"

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///brightbook"
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)