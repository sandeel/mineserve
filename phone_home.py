import requests
import datetime

instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
print instance_id

r = requests.get('http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/server_data?instance_id='+instance_id)

expiry_date = datetime.datetime.strptime(r.json()['expiry_date'], "%Y-%m-%d %H:%M:%S.%f")

td = expiry_date - datetime.datetime.now()

print(td.seconds // 3600)

