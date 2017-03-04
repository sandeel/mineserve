import os
from mineserve import application
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        application.config['STUB_AWS_RESOURCES'] = True
        self.app = application.test_client()

    def tearDown(self):
        pass

    def test_empty_db(self):
        assert 'No' in 'No entries'

if __name__ == '__main__':
    unittest.main()
