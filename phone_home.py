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

print("Getting server data for instance...")
r = requests.get('http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/server_data?instance_id='+instance_id)

expiry_date = datetime.datetime.strptime(r.json()['expiry_date'], "%Y-%m-%d %H:%M:%S.%f")
print("Expiry date is %s" % expiry_date)

td = expiry_date - datetime.datetime.now()

seconds_left = td.seconds
hours_left = td.seconds // 3600

if expiry_date < datetime.datetime.now():
    print("Server expired. Terminating instance.")
    client = boto3.client('ec2', region_name=region)
    response = client.terminate_instances(
        InstanceIds=[
	    instance_id,
        ]
)
elif hours_left < 1:
    print("WARNING. Server will be terminated in less than an hour unless topped-up. All data will be lost.")
elif hours_left < 5:
    message =("WARNING. 5 hours credit remaining on this server.")
    Popen(['/home/ubuntu/mcrcon/mcrcon', '-H', 'localhost', '-P', '19132', '-p', 'password', 'say '+message])
