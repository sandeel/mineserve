import requests
import datetime
from subprocess import Popen
import boto3
import filecmp
import time
from random import randint
import subprocess
import json

phone_home_endpoint = str(open('/home/ubuntu/config.json').read()['phone_home_endpoint'])

print("Getting instance id...")
instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
print("Instance id is "+instance_id)
print("Getting region...")
region = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document').json()['region']
print("Region is "+region)

seconds = randint(0,3300)
print("Waiting "+str(seconds)+" seconds before phoning home...")
time.sleep(seconds)

print("Phoning home...")
server_message = requests.get(phone_home_endpoint+'/api/v0.1/phone_home?instance_id='+instance_id).json()['server_message']

server_id = requests.get(phone_home_endpoint+'/server_data?instance_id='+instance_id).json()['id']

server_message = requests.get(phone_home_endpoint+'/api/v0.1/phone_home?instance_id='+instance_id).json()['server_message']

if server_message:
    print('Sending server message: '+server_message)

Popen(['/home/ubuntu/mcrcon/mcrcon', '-H', 'localhost', '-P', '19132', '-p', 'password', 'say '+server_message])

# check if properties have changed
subprocess.call(['curl', phone_home_endpoint+'/server/'+server_id+'/properties', '-o', '/home/ubuntu/server.properties'])

properties0 = open("/home/ubuntu/server.properties","r")
properties1 = open("/home/ubuntu/server.properties.bk","r")

lines1 =properties0.readlines()

for i,lines2 in enumerate(properties1):
    if lines2 != lines1[i]:
        message = "Server configuration changed, rebooting in one minute."
        print(message)
        Popen(['/home/ubuntu/mcrcon/mcrcon', '-H', 'localhost', '-P', '19132', '-p', 'password', 'say '+message])
        time.sleep(60)
        Popen(['cp', '/home/ubuntu/server.properties', '/home/ubuntu/server.properties.bk'])
        client = boto3.client('ec2', region_name=region)
        client.reboot_instances(InstanceIds=[instance_id,])
    else:
        print("line "+  str(i) +" matches")

