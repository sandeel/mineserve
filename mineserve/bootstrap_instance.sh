#!/bin/bash

HOME=/home/ubuntu


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
curl -kL https://github.com/sandeel/mineserve/archive/master.zip  -o /tmp/master.zip
unzip master.zip


docker stop atlas

cd /home/ubuntu

read RESOURCES_ENDPOINT <<< $(cat /home/ubuntu/config.json | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["resources_endpoint"]')
echo Resources endpoint is $RESOURCES_ENDPOINT

# get genisys
cd $HOME
rm -rf genisys.phar
wget --no-check-certificate --no-proxy $RESOURCES_ENDPOINT/genisys.phar

# copy genisys
cp /tmp/mineserve-master/resources/genisys.yml /home/ubuntu/genisys.yml

# copy phone home
cp /tmp/mineserve-master/phone_home.py /home/ubuntu/phone_home.py

# copy pocketmine.yml
cp /tmp/mineserve-master/resources/pocketmine.yml /home/ubuntu/pocketmine.yml

#get server properties
read INSTANCE_ID <<< $(curl -k 'http://169.254.169.254/latest/meta-data/instance-id')
echo Instance ID is $INSTANCE_ID
read PHONE_HOME_ENDPOINT <<< $(cat /home/ubuntu/config.json | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["phone_home_endpoint"]')
echo Phone home endpoint is $PHONE_HOME_ENDPOINT
read SERVER_ID <<< $(curl -k -s ${PHONE_HOME_ENDPOINT}/server_data?instance_id=${INSTANCE_ID} | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["id"]')
read PLUGINS <<< $(curl -k -s ${PHONE_HOME_ENDPOINT}/server_data?instance_id=${INSTANCE_ID} | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["enabled_plugins"]')


echo Server ID is $SERVER_ID

cd $HOME
rm -rf server.properties
wget --no-check-certificate --no-proxy ${PHONE_HOME_ENDPOINT}/server/${SERVER_ID}/properties -O server.properties
cp /home/ubuntu/server.properties /home/ubuntu/server.properties.bk

#op the user
read OPS <<< $(curl -k -s ${PHONE_HOME_ENDPOINT}/server_data?instance_id=${INSTANCE_ID} | python -c 'import json,sys;obj=json.load(sys.stdin);print obj["op"]')
echo Ops are $OPS
echo $OPS > /home/ubuntu/ops.txt

#copy the plugins
mkdir /home/ubuntu/plugins
rm -rf /home/ubuntu/plugins/*.phar
chmod 777 -R /home/ubuntu/plugins
cd /home/ubuntu/plugins
for i in ${PLUGINS//,/ }
do
    wget --no-check-certificate --no-proxy $RESOURCES_ENDPOINT/plugins/$i
done

# start or run container
docker run -itd --name atlas --restart always -p 33775:33775 -p 33775:33775/udp -v /home/ubuntu/genisys.yml:/srv/genisys/genisys.yml -v /home/ubuntu/plugins:/srv/genisys/plugins -v /home/ubuntu/ops.txt:/srv/genisys/ops.txt -v /home/ubuntu/genisys.phar:/srv/genisys/genisys.phar -v /home/ubuntu/server.properties:/srv/genisys/server.properties -v /home/ubuntu/pocketmine.yml:/srv/genisys/pocketmine.yml itxtech/docker-env-genisys || docker restart atlas

#docker restart atlas

#mcrcon
#cd /home/ubuntu
#rm -rf mcrcon && git clone https://github.com/Tiiffi/mcrcon.git && cd mcrcon && gcc -pedantic -Wall -Wextra -O2 -s -o mcrcon mcrcon.c

#reload plugins
#cd /home/ubuntu
#sleep 20
#/home/ubuntu/mcrcon/mcrcon -H localhost -P 33775 -p password reload

pip install requests
pip install boto3