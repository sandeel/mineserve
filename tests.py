import os
from mineserve import application
from mineserve import views
import unittest
import tempfile
import json
import subprocess
import datetime
import time

table_identifier = str(datetime.datetime.now())

server_id = None

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        if application.config['STUB_AWS_RESOURCES']:
            print('Creating test database...')
            subprocess.call(['aws dynamodb create-table \
                            --endpoint-url http://localhost:8000 \
                            --region eu-west-1 \
                            --attribute-definitions AttributeName=id,AttributeType=S AttributeName=user,AttributeType=S \
                            --key-schema AttributeName=id,KeyType=HASH \
                            --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1 \
                            --global-secondary-indexes IndexName=user-index,KeySchema=\"{AttributeName=\'user\',KeyType=HASH}\",Projection={ProjectionType=ALL},ProvisionedThroughput=\"{ReadCapacityUnits=1,WriteCapacityUnits=1}\" \
                            --table-name msv-testing-servers 1> /dev/null'],
                            shell=True)

    def tearDown(self):
        if application.config['STUB_AWS_RESOURCES']:
            print('Deleting test database...')
            subprocess.call(['aws dynamodb delete-table \
                            --region eu-west-1 \
                            --table-name msv-testing-servers \
                            --endpoint-url http://localhost:8000 1> /dev/null'],
                            shell=True)

    def test_servers(self):
        with views.user_set(application, 'testuser'):
            with application.test_client() as c:
                resp = c.get('/api/0.1/servers')
                assert b'\"servers\": []' in resp.data

                resp = c.post('/api/0.1/servers', data=json.dumps(dict(
                    name='Testing Server',
                    type='ark_server',
                    size='large',
                    region='us-east-1'
                )),
                content_type='application/json')
                assert b'\"name\": \"Testing Server\"' in resp.data
                global server_id
                server_id = json.loads(resp.get_data(as_text=True))['id']

                print(server_id)
                resp = c.delete('/api/0.1/servers/'+server_id)

if __name__ == '__main__':
    unittest.main()
