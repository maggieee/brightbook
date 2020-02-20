from unittest import TestCase
from server import app

class FlaskTests(TestCase):

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

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
    #     self.assertIn(b"View everyone on BrightBook", result.data)