FROM 137112412989.dkr.ecr.eu-west-1.amazonaws.com/amazonlinux:latest

RUN yum update -y

RUN yum upgrade -y

RUN yum install -y git libtool-libs wget tar

RUN git clone --recursive https://github.com/pmmp/pocketmine-mp.git pocketmine

WORKDIR /pocketmine

RUN git checkout mcpe-1.0

RUN wget https://bintray.com/pocketmine/PocketMine/download_file?file_path=PHP_7.0.6_x86-64_Linux.tar.gz -O php.tar.gz

RUN tar zxvf php.tar.gz

RUN rm php.tar.gz

WORKDIR /pocketmine

EXPOSE 19132/udp

ENTRYPOINT ["./start.sh", "--no-wizard"]
