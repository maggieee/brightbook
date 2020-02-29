"""Utility file to seed brightbook database/"""

from sqlalchemy import func
from models import User, Post, Heart, Company

from models import connect_to_db, db
from server import app

from datetime import datetime


def kaboom():
    """Clear out User, Post, and Heart tables"""

    print("Kaboom")

    Heart.query.delete()
    Post.query.delete()
    User.query.delete()


def load_users():
    """Load users from u.user into database."""

    print("Users")

    # Read users.txt file and insert data
    for row in open("seed_data/users.txt"):
        row = row.rstrip()
        user_id, email, display_name = row.split("|")

        user = User(user_id=user_id,
                    email=email,
                    display_name=display_name)
        user.set_password('password')

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_posts():
    """Load posts from posts.txt into database."""

    print("Posts")

    # Read posts.txt file and insert data
    for row in open("seed_data/posts.txt"):
        row = row.rstrip()
        post_id, user_id, post_text = row.split("|")

        post = Post(post_id=post_id,
                    user_id=user_id,
                    post_text=post_text)

        # We need to add to the session or it won't ever be stored
        db.session.add(post)

    # Once we're done, we should commit our work
    db.session.commit()


def load_hearts():
    """Load hearts from hearts.txt into database."""

    print("Hearts")

    # Read posts.txt file and insert data
    for row in open("seed_data/hearts.txt"):
        row = row.rstrip()
        heart_id, user_id, post_id, heart_type = row.split("|")

        heart = Heart(heart_id=heart_id,
                    user_id=user_id,
                    post_id=post_id,
                    heart_type=heart_type)

        # We need to add to the session or it won't ever be stored
        db.session.add(heart)

    # Once we're done, we should commit our work
    db.session.commit()

def load_companies():
    """Load companies from companies.txt into database."""

    print("Companies")

    # Read posts.txt file and insert data
    for row in open("seed_data/companies.txt"):
        row = row.rstrip()
        company_id, company_name, hired_bootcamp_grads, hired_hackbrighters, job_listings_link = row.split("|")

        if hired_bootcamp_grads == "y":
            hired_bootcamp_grads = True
        else:
            hired_bootcamp_grads = False

        if hired_hackbrighters == "y":
            hired_hackbrighters = True
        else:
            hired_hackbrighters = False

        company = Company(company_id=company_id,
                    company_name=company_name,
                    hired_bootcamp_grads=hired_bootcamp_grads,
                    hired_hackbrighters=hired_hackbrighters,
                    job_listings_link=job_listings_link)

        # We need to add to the session or it won't ever be stored
        db.session.add(company)

    # Once we're done, we should commit our work
    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

def set_val_post_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(Post.post_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('posts_post_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

def set_val_heart_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(Heart.heart_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('hearts_heart_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

def set_val_company_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(Company.company_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('companies_company_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    kaboom()
    # Import different types of data
    load_users()
    load_posts()
    load_hearts()
    load_companies()
    set_val_user_id()
    set_val_post_id()
    set_val_heart_id()
    set_val_company_id()