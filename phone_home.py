import requests

r = requests.get('http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/server_data?instance_id=i-31d90dec')

expiry_date = datetime.datetime.strptime(r['expiry_date'], "%Y-%m-%d %H:%M:%S.%f")

print
