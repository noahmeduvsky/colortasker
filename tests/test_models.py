import unittest
from app import create_app
from extensions import db
from models.user import User

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        self.user = User(name='testuser', email='test@example.com', password='password')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        self.assertTrue(self.user.check_password('password'))
        self.assertFalse(self.user.check_password('wrongpassword'))

    def test_unique_username(self):
        db.session.add(self.user)
        db.session.commit()
        duplicate_user = User(name='testuser', email='test2@example.com', password='password')
        db.session.add(duplicate_user)
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
