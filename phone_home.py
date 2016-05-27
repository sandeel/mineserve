import requests
import datetime
from subprocess import Popen
import boto3
import filecmp
import time
from random import randint

print("Getting instance id...")
instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
print("Instance id is "+instance_id)
print("Getting region...")
region = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document').json()['region']
print("Region is "+region)

seconds = randint(0,3300)
print("Waiting "+seconds+" seconds before phoning home...")
time.sleep(seconds)

print("Phoning home...")
server_message = requests.get('http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/api/v0.1/phone_home?instance_id='+instance_id).json()['server_message']

server_id = requests.get('http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/server_data?instance_id='+instance_id).json()['id']

Popen(['cp', '/home/ubuntu/server.properties', '/home/ubuntu/server.properties.bk'])
Popen(['curl', 'http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/server/'+server_id+'/properties', '-o', '/home/ubuntu/server.properties'])

if open('/home/ubuntu/server.properties','r').read() != open('/home/ubuntu/server.properties.bk','r').read():
    print("New config file, rebooting")
    client = boto3.client('ec2', region_name=region)
    client.reboot_instances(InstanceIds=[instance_id,])

server_message = requests.get('http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/api/v0.1/phone_home?instance_id='+instance_id).json()['server_message']

if server_message:
    print('Sending server message: '+server_message)

    Popen(['/home/ubuntu/mcrcon/mcrcon', '-H', 'localhost', '-P', '19132', '-p', 'password', 'say '+server_message])
