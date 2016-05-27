import requests
import datetime
from subprocess import Popen
import boto3

print("Getting instance id...")
instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
print("Instance id is "+instance_id)
print("Getting region...")
region = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document').json()['region']
print("Region is "+region)

print("Phoning home...")
server_message = requests.get('http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/phone_home?instance_id='+instance_id).json()['server_message']

if server_message:

    Popen(['/home/ubuntu/mcrcon/mcrcon', '-H', 'localhost', '-P', '19132', '-p', 'password', 'say '+server_message])
