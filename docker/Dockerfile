FROM 137112412989.dkr.ecr.eu-west-1.amazonaws.com/amazonlinux:latest

RUN yum update -y

RUN yum upgrade -y

RUN yum install -y git libtool-libs wget tar

RUN git clone --recursive https://github.com/pmmp/pocketmine-mp.git pocketmine-mp.git

WORKDIR pocketmine-mp.git

RUN wget https://bintray.com/pocketmine/PocketMine/download_file?file_path=PHP_7.0.6_x86-64_Linux.tar.gz -O php.tar.gz

RUN tar zxvf php.tar.gz

RUN rm php.tar.gz

EXPOSE 19132/udp

ENTRYPOINT ["./start.sh", "--no-wizard"]
