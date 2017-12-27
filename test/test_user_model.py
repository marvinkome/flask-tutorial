import unittest
from app.models import User

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