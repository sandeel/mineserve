#!/bin/bash

HOME=/home/ubuntu

# install docker
cd $HOME
curl -sSL https://get.docker.com/ | sh

# compile working git version
apt-get -y install build-essential fakeroot dpkg-dev  
rm -Rf /root/git-openssl
mkdir /root/git-openssl
cd /root/git-openssl 
apt-get source git
apt-get -y build-dep git  
apt-get -y install libcurl4-openssl-dev  
dpkg-source -x git_*.dsc                 
cd git-*                
sed -i s/libcurl4-gnutls-dev/libcurl4-openssl-dev/g debian/control
sed -i "s/TEST =test//g" debian/rules                             
dpkg-buildpackage -rfakeroot -b      
dpkg -i ../git_*_amd64.deb
rm -R git*

# configure git
apt-get -y install python-pip
pip install awscli
cd $HOME
: > .gitconfig
echo "[credential]" > .gitconfig
echo '  helper = !aws codecommit credential-helper $@' >> .gitconfig
echo "  UseHttpPath = true" >> .gitconfigo

# clone repo
HTTPS_REPO_URL=https://git-codecommit.us-east-1.amazonaws.com/v1/repos/mineserve
git clone https://chromium.googlesource.com/chromium/tools/depot_tools
export PATH=`pwd`/depot_tools:"$PATH"
rm -Rf mineserve
git-retry -v clone ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/mineserve

docker stop new-atlas6

# get phar
curl https://gitlab.com/itxtech/genisys/builds/1461919/artifacts/file/Genisys_1.1dev-93aea9c.phar -o genisys.phar

# start or run container
docker run -itd --name new-atlas6 -p 19132:19132 -p 19132:19132/udp -v /home/ubuntu/genisys.phar:/srv/genisys/genisys.phar -v /home/ubuntu/server.properties:/srv/genisys/server.properties -v /home/ubuntu/genisys.yml:/srv/genisys/genisys.yml --restart=unless-stopped itxtech/docker-env-genisys || docker start new-atlas6

# install mcrcon
cd $HOME
rm -r mcrcon
git retry -v clone https://github.com/Tiiffi/mcrcon.git
cd mcrcon
gcc -std=gnu11 -pedantic -Wall -Wextra -O2 -s -o mcrcon mcrcon.c

cd $HOME
./mcrcon/mcrcon -c -H localhost -P 19132 -p password "say hello"
