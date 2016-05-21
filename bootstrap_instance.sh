#!/bin/bash

HOME=/home/ubuntu

# install docker
cd $HOME
curl -sSL https://get.docker.com/ | sh
curl https://gitlab.com/itxtech/genisys/builds/1452305/artifacts/file/Genisys_1.1dev-a685f20.phar -o genisys.phar


# compile working git version
apt-get -y install build-essential fakeroot dpkg-dev  
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
echo "[credential]" > .gitconfig
echo '  helper = !aws codecommit credential-helper $@' >> .gitconfig
echo "  UseHttpPath = true" >> .gitconfig

# clone repo
HTTPS_REPO_URL=https://git-codecommit.us-east-1.amazonaws.com/v1/repos/mineserve
git clone $HTTPS_REPO_URL
