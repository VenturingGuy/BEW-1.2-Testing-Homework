import os
from unittest import TestCase

from datetime import date
 
from books_app import app, db, bcrypt
from books_app.models import Book, Author, User, Audience

"""
Run these tests with the command:
python -m unittest books_app.main.tests
"""

#################################################
# Setup
#################################################

def create_books():
    a1 = Author(name='Harper Lee')
    b1 = Book(
        title='To Kill a Mockingbird',
        publish_date=date(1960, 7, 11),
        author=a1
    )
    db.session.add(b1)

    a2 = Author(name='Sylvia Plath')
    b2 = Book(title='The Bell Jar', author=a2)
    db.session.add(b2)
    db.session.commit()

def create_user():
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""
 
    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        """Tests for user signup."""

        p_data = {'username': 'test_user', 'password': 'testpass'}
        self.app.post('/signup', data=p_data)
        signup_user = User.query.filter_by(username="test_user").one()
        self.assertEqual(signup_user.username, "test_user")

    def test_signup_existing_user(self):
        """Tests for signup for an existing user, returning a message indicating the username already exists."""

        create_user()
        p_data = {'username': 'me1', 'password': 'testpass'}
        response = self.app.post('/signup', data=p_data)
        response_text = response.get_data(as_text=True)
        self.assertIn('That username is taken. Please choose a different one.', response_text)

    def test_login_correct_password(self):
        """Tests for user login."""

        create_user()
        p_data = {'username': 'me1', 'password': 'password'}
        response = self.app.post('/login', data=p_data)
        response_text = response.get_data(as_text=True)
        self.assertNotIn('Log In', response_text)
        self.assertNotIn('Sign Up', response_text)
        

    def test_login_nonexistent_user(self):
        """Tests for user login, returning a message that indicates the user doesn't exist (hasn't signed up)."""

        p_data = {'username': 'me1', 'password': 'password_hash'}
        response = self.app.post('/login', data=p_data)
        response_text = response.get_data(as_text=True)
        self.assertIn('No user with that username. Please try again.', response_text)

    def test_login_incorrect_password(self):
        """Tests for user login, returning a message indicating that the password is incorrect."""

        create_user()
        p_data = {'username': 'me1', 'password': 'testpass'}
        response = self.app.post('/login', data=p_data)
        response_text = response.get_data(as_text=True)

        # Note: I changed the assert message to remove the contraction. This is also reflected in the forms.py file.
        self.assertIn('Password does not match. Please try again.', response_text)

    def test_logout(self):
        """Tests for user logging out."""

        create_user()
        p_data = {'username': 'test_user5', 'password': 'testpass5'}
        self.app.post('/login', data=p_data)
        response = self.app.post('/logout', follow_redirects=True)

        response_text = response.get_data(as_text=True)
        self.assertNotIn('Log In', response_text)
        self.assertNotIn('Sign Up', response_text)


