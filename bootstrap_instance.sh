#!/bin/bash

HOME=/home/ubuntu

# install docker
cd $HOME
curl -sSL https://get.docker.com/ | sh

# install git
apt-get install -y git

# pip
apt-get -y install python-pip
pip install awscli




# from home run or start docker

# pull zip of code from s3
apt-get -y install unzip
cd /tmp
rm -Rf /tmp/mineserve-master
curl -L https://github.com/sandeel/mineserve/archive/master.zip  -o /tmp/master.zip
unzip master.zip


docker stop atlas

# copy the phar from /tmp to home
cp /tmp/mineserve-master/resources/genisys.phar /home/ubuntu/genisys.phar

# if not server.properties copy it to home
cp -n /tmp/mineserve-master/resources/genisys.yml /home/ubuntu/genisys.yml

# if not server.properties copy it to home
cp -n /tmp/mineserve-master/resources/pocketmine.yml /home/ubuntu/pocketmine.yml


#get server properties
read INSTANCE_ID <<< $(curl 'http://169.254.169.254/latest/meta-data/instance-id')
echo Instance ID is $INSTANCE_ID
read SERVER_ID <<< $(curl -s http://52.30.111.108:5000/server_data?instance_id=${INSTANCE_ID} | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["id"]')
echo Server ID is $SERVER_ID

curl http://ec2-52-30-111-108.eu-west-1.compute.amazonaws.com:5000/server/$SERVER_ID/properties -o server.properties
cp /home/ubuntu/server.properties /home/ubuntu/server.properties.bk

#op the user
echo """+self.op+""" > /home/ubuntu/ops.txt

# start or run container
docker run -itd --name atlas -p 19132:19132 -p 19132:19132/udp -v /home/ubuntu/plugins:/srv/genisys/plugins -v /home/ubuntu/ops.txt:/srv/genisys/ops.txt -v /home/ubuntu/genisys.phar:/srv/genisys/genisys.phar -v /home/ubuntu/server.properties:/srv/genisys/server.properties -v /home/ubuntu/genisys.yml:/srv/genisys/genisys.yml -v /home/ubuntu/pocketmine.yml:/srv/genisys/pocketmine.yml --restart=unless-stopped itxtech/docker-env-genisys || docker start atlas

# install mcrcon
cd $HOME
rm -rf mcrcon
git retry -v clone https://github.com/Tiiffi/mcrcon.git
cd mcrcon
gcc -std=gnu11 -pedantic -Wall -Wextra -O2 -s -o mcrcon mcrcon.c

# set up cron to phone home
pip install requests
pip install boto3
echo "0 */1 * * * root python /home/ubuntu/mineserve/phone_home.py" >> /etc/crontab
