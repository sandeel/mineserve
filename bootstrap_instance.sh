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

# clone repo
HTTPS_REPO_URL=https://git-codecommit.us-east-1.amazonaws.com/v1/repos/mineserve
git clone https://chromium.googlesource.com/chromium/tools/depot_tools
export PATH=`pwd`/depot_tools:"$PATH"
rm -Rf mineserve
git-retry -v clone https://github.com/sandeel/mineserve.git

docker stop atlas

# get phar
curl https://gitlab.com/itxtech/genisys/builds/1461919/artifacts/file/Genisys_1.1dev-93aea9c.phar -o genisys.phar

# start or run container
docker run -itd --name atlas -p 19132:19132 -p 19132:19132/udp -v /home/ubuntu/genisys.phar:/srv/genisys/genisys.phar -v /home/ubuntu/mineserve/server.properties:/srv/genisys/server.properties -v /home/ubuntu/mineserve/genisys.yml:/srv/genisys/genisys.yml --restart=unless-stopped itxtech/docker-env-genisys || docker start atlas

# install mcrcon
cd $HOME
rm -r mcrcon
git retry -v clone https://github.com/Tiiffi/mcrcon.git
cd mcrcon
gcc -std=gnu11 -pedantic -Wall -Wextra -O2 -s -o mcrcon mcrcon.c

cd $HOME
#./mcrcon/mcrcon -c -H localhost -P 19132 -p password "say hello"


echo "Going down for reboot..."
reboot
