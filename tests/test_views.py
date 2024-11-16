import unittest
from app import create_app
from extensions import db
from models.user import User

class ViewTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signup(self):
        response = self.client.post('/auth/signup', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password',
            'confirm_password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(name='testuser').first()
        self.assertIsNotNone(user)

    def test_login_logout(self):
        user = User(name='testuser', email='test@example.com', password='password')
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Log In', response.data)

if __name__ == '__main__':
    unittest.main()
