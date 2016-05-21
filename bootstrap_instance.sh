#!/bin/bash

cd /home/ubuntu
curl -sSL https://get.docker.com/ | sh
curl https://gitlab.com/itxtech/genisys/builds/1452305/artifacts/file/Genisys_1.1dev-a685f20.phar -o genisys.phar


apt-get -y install git
git clone ...... /tmp/


# codedeploy agent
apt-get -y update
apt-get -y install awscli
apt-get -y install ruby2.0
cd /home/ubuntu
aws s3 cp s3://aws-codedeploy-us-west-2/latest/install . --region us-west-2
chmod +x ./install
./install auto
