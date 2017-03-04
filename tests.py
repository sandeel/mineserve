import os
from mineserve import application
from mineserve import views
import unittest
import tempfile
import json

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        application.config['STUB_AWS_RESOURCES'] = True

    def tearDown(self):
        pass

    def test_010_get_empty_servers(self):
        with views.user_set(application, 'testuser'):
            with application.test_client() as c:
                resp = c.get('/api/0.1/servers')
                assert b'\"servers\": []' in resp.data

    def test_020_create_server(self):
        with views.user_set(application, 'testuser'):
            with application.test_client() as c:
                resp = c.post('/api/0.1/servers', data=json.dumps(dict(
                    name='Testing Server',
                    type='ark_server',
                    size='large'
                )),
                content_type='application/json')

if __name__ == '__main__':
    unittest.main()
