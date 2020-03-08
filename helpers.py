from flask import (Flask, request, session)

from models import User, Post, Heart, HiringPost, db, connect_to_db


def add_and_commit_thing_to_database(thing):
    """Add and commit something to the db"""

    db.session.add(thing)
    db.session.commit()


def delete_db_object(db_model) -> None:
    """Delete and commit the passed in sql alchemy model
    """
    db.session.delete(db_model)
    db.session.commit()
    return

def create_new_hiring_post_from_summernote(user):
    """Create a new post using the summernote WYSIWYG editor"""

    ### FIX ME: future sprint - vulnerabiity issues ###
    # cleaned_post = bleach.clean(request.form.get('editordata'),
    #     tags=bleach.sanitizer.ALLOWED_TAGS + ['div', 'br', 'span', 'p', 'h1',
    #     'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'u'])

    return HiringPost(display_name=user.display_name, post_text=request.form.get('editordata'))


def create_new_post_from_summernote(user):
    """Create a new post using the summernote WYSIWYG editor"""

    ### FIX ME: future sprint - vulnerabiity issues ###
    # cleaned_post = bleach.clean(request.form.get('editordata'),
    #     tags=bleach.sanitizer.ALLOWED_TAGS + ['div', 'br', 'span', 'p', 'h1',
    #     'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'u'])

    return Post(display_name=user.display_name, post_text=request.form.get('editordata'))


def get_current_user_from_session():
    """Use email in session to get current user from db"""

    email = session['email']
    user = User.query.filter_by(email=email).first_or_404()

    return user
