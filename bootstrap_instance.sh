#!/bin/bash

cd /home/ubuntu
curl -sSL https://get.docker.com/ | sh
curl https://gitlab.com/itxtech/genisys/builds/1452305/artifacts/file/Genisys_1.1dev-a685f20.phar -o genisys.phar


apt-get -y install git
git clone ...... /tmp/
