import unittest
import time
from app.models import User, db

class UserModelTest(unittest.TestCase):
    def test_password_setter(self):
        u = User(password='radius')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='radius')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='radius')
        self.assertTrue(u.verify_password('radius'))
        self.assertFalse(u.verify_password('diamond'))

    def test_password_salts_are_random(self):
        u = User(password='radius')
        u2 = User(password='radius')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confimation(self):
        u = User(password='radius')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(expire=10)
        self.assertTrue(u.confirm(token))

    def test_invalid_confimation(self):
        u = User(password='radius')
        u2 = User(password='radius')
        db.session.add(u)
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(expire=10)
        self.assertFalse(u2.confirm(token))

    def test_expired_confimation(self):
        u = User(password='radius')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(expire=1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))