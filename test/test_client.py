import unittest
import re
import json
from base64 import b64encode
from app import create_app, db
from app.models import User, Role
from flask import url_for, current_app

class FlaskClientTest(unittest.TestCase):
    def setUp(self):
        """Set up client test
        """
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        """Tear down client test
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exist(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertTrue('Welcome to Flasky' in response.get_data(as_text=True))

    def test_register_login(self):

        # register account
        response = self.client.post(url_for('auth.register'), data={
            'email': 'anony@mous.me',
            'username': 'annie',
            'password': 'cat',
            'password2': 'cat'
        })
        self.assertTrue(response.status_code == 302)

        # login
        response = self.client.post(url_for('auth.login'), data={
            'email': 'anony@mous.me',
            'password': 'cat'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue(re.search('Hello,\s+annie!', data))
        self.assertTrue('You have not confirmed your account' in data)

        # confirm account
        user = User.query.filter_by(email='anony@mous.me').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('You are confirmed' in data)

        # logout
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertTrue('You have been logged out' in data)

    def get_api_header(self, username, password):
        return {
            'Authorization':
                'Basic ' + b64encode((username+':'+password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type':'application/json'
        }

    def test_api(self):
        
        # no auth test
        response = self.client.post(
            url_for('api.get_posts'),
            data=json.dumps({'body':'Blog body'}),
            content_type='application/json'
        )
        self.assertTrue(response.status_code == 403)

    def test_api_posts(self):
        
        # add a user
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)
        u = User(email='sec@john.me', password='kilo', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()
        u = User.query.filter_by(email='sec@john.me').first()
        self.assertIsNotNone(u)

        # get token 
        response = self.client.get(
            url_for('api.get_token'),
            headers = self.get_api_header('sec@john.me','kilo'),
        )

        json_response = json.loads(response.data.decode('utf-8'))
        token = json_response['token']
        self.assertIsNotNone(token)


        # write a post
        response = self.client.post(
            url_for('api.new_post'),
            headers = self.get_api_header('sec@john.me','kilo'),
            data = json.dumps({'body':'Blog body'})
        )
        self.assertTrue(response.status_code == 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # get the new post
        response = self.client.get(
            url,
            headers=self.get_api_header(token,'')
        )
        self.assertTrue(response.status_code == 200)
        json_response = json.loads(response.data.decode('utf-8'))
        self.assertTrue(json_response['url'] == url)
        self.assertTrue(json_response['body'] == 'Blog body')
        self.assertTrue(json_response['body_html'] == '<p>Blog body</p>')
