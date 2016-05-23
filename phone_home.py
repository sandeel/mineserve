import requests
import datetime

echo "Getting instance id..."
instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
echo "Instance id is "+instance_id

echo "Getting server data for instance..."
r = requests.get('http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/server_data?instance_id='+instance_id)

expiry_date = datetime.datetime.strptime(r.json()['expiry_date'], "%Y-%m-%d %H:%M:%S.%f")
echo "Expiry date is "+expiry date

hours_left = td.seconds // 3600

if hours_left < 1:
    echo "..."
elif hours_left < 5:
    echo "WARNING. 5 hours credit remaining. Terminated server will be irretrievable."
