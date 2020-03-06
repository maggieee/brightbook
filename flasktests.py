from unittest import TestCase
from server import app
from models import connect_to_db, db, User
from seeds import load_users

class FlaskTests(TestCase):

    def setUp(self):
        """Stuff to do before every test."""

        app.config['TESTING'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        self.client = app.test_client()
        connect_to_db(app, db_uri='postgresql:///testdb')
        db.create_all()

        #example_data will error out atm, need to create
        load_users()

        # bird = Bird(species="bluebird", 
        #             scientific_name="reallyo scientifico bluebirdius")
        # db.session.add(bird)
        # db.session.commit()

    # def tearDown(self):
    #     """Stuff to do after tests."""

    #     db.session.remove()
    #     db.drop_all()

    def test_logged_out_homepage(self):
        """Check that the homepage loads for a logged-out user."""

        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn(b"Log in or register", result.data)

    # def test_login(self):
    #     """Check that a user can log in."""

    #     result = self.client.post("/login",
    #                               data={"email": "test2@test.com", "password": "password"},
    #                               follow_redirects=True)
    #     self.assertIn(b"Write new post", result.data)

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


if __name__ == '__main__':
    unittest.main()