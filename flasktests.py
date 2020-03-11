import unittest
from unittest import TestCase
from server import app
from models import connect_to_db, db, User
from seeds import load_users, load_posts


class FlaskTests(TestCase):

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.client = app.test_client()
        connect_to_db(app, db_uri='postgresql:///testdb')
        db.create_all()

        load_users()

    def tearDown(self):
        """Stuff to do after tests."""

        db.session.remove()
        db.drop_all()

    def test_logged_out_homepage(self):
        """Check that the homepage loads for a logged-out user."""

        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"The future's so bright", result.data)

    def test_login_page(self):
        """Check that the login page loads for a logged-out user."""

        result = self.client.get('/login')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Log in to your account", result.data)

    def test_register_page(self):
        """Check that the register page loads for a logged-out user."""

        result = self.client.get('/register')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Register for a new account", result.data)

    def test_login(self):
        """Check that a user can log in."""

        result = self.client.post("/login",
                                  data={"email": "test2@test.com", "password": "password"},
                                  follow_redirects=True)
        self.assertIn(b"Write new post", result.data)

    def test_homepage_again(self):
        """Test homepage initial rendering"""

        # Setting user_id for current session.
        with self.client.session_transaction() as sess:
            sess['email'] = "test2@test.com"

        result = self.client.get('/', follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Write new post", result.data)

    def test_browse_users(self):
        """Test homepage initial rendering"""

        # Setting user_id for current session.
        with self.client.session_transaction() as sess:
            sess['email'] = "test2@test.com"

        result = self.client.get('/users', follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Community Directory", result.data)

    def test_user_profile(self):
        """Test user profile rendering"""

        # Setting user_id for current session.
        with self.client.session_transaction() as sess:
            sess['email'] = "test2@test.com"

        result = self.client.get('/users/Cornelia%20Person', follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"About Cornelia Person", result.data)

    def test_create_message(self):
        """Test create message page rendering"""

        # Setting user_id for current session.
        with self.client.session_transaction() as sess:
            sess['email'] = "test2@test.com"

        result = self.client.get('/create_message/4', follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Write a new message to", result.data)

    # def test_post_details(self):
    #     """Test that post details page renders."""

    #     # Setting user_id for current session.
    #     with self.client.session_transaction() as sess:
    #         sess['email'] = "test2@test.com"

    #     result = self.client.get('/posts/10', follow_redirects=True)
    #     self.assertEqual(result.status_code, 200)
    #     self.assertIn(b"Heart!", result.data)

    def test_create_new_post(self):
        """Test that the write a post page renders."""

        # Setting user_id for current session.
        with self.client.session_transaction() as sess:
            sess['email'] = "test2@test.com"

        result = self.client.get('/create_post', follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Write New Post", result.data) 

    def test_load_companies(self):
        """Test that the companies page renders."""

        # Setting user_id for current session.
        with self.client.session_transaction() as sess:
            sess['email'] = "test2@test.com"

        result = self.client.get('/companies', follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Submit a new company", result.data) 

    def test_create_company(self):
        """Test that the create company page renders."""

        # Setting user_id for current session.
        with self.client.session_transaction() as sess:
            sess['email'] = "test2@test.com"

        result = self.client.get('/create_company', follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Add company", result.data)

    def test_hiring_posts(self):
        """Test that the Hiring Posts page renders."""

        with self.client.session_transaction() as sess:
            sess['email'] = "test2@test.com"

        result = self.client.get('/hiring_posts', follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Write new hiring post", result.data)

    def test_create_hiring_post_page(self):
        """Test that the create hiring post page renders."""

        with self.client.session_transaction() as sess:
            sess['email'] = "test2@test.com"

        result = self.client.get('/create_hiring_post', follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Write New Hiring Post", result.data)
    
    # def test_send_message(self):
    #     """Check that a user can send a message."""

    #     # Setting user_id for current session.
    #     with self.client.session_transaction() as sess:
    #         sess['email'] = "test2@test.com"

    #     result = self.client.post("/create_message/4",
    #                               data={"subject": "hello"},
    #                               follow_redirects=True)
    #     self.assertIn(b"Message sent to User 4!", result.data)

if __name__ == '__main__':
    unittest.main()