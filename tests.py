import os
from mineserve import application
from mineserve import views
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        application.config['STUB_AWS_RESOURCES'] = True

    def tearDown(self):
        pass

    def test_empty_db(self):
        assert 'No' in 'No entries'

        with views.user_set(application, 'testuser'):
            with application.test_client() as c:
                resp = c.get('/api/0.1/servers')
                print(resp)

if __name__ == '__main__':
    unittest.main()
