from mineserve import application
import datetime
from datetime import timezone
import uuid
import random
import boto3
import time
import math
from threading import Thread
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, UTCDateTimeAttribute
import string
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import NumberAttribute
import pytz

class User():
    """ User of site site (Cognito)
    """

    def __init__(self, username):
        client = boto3.client('cognito-idp', region_name=application.config['AWS_REGION'])

        try:
            response = client.admin_get_user(
                UserPoolId=application.config['POOL_ID'],
                Username=username
            )
            self.username = response['Username']

        except:
            raise ValueError("User doesn't exist in cognito")

    def serialize(self):
        return {
            "username": self.id
        }

    def __str__(self):
        return self.username


class PromoCode(Model):
    """ Promo Code for the site
    Can have various uses including free top-up time
    """

    class Meta:
        region = application.config['AWS_REGION']
        table_name = str(application.config['APP_NAME'])+'-promocodes'

    code = UnicodeAttribute(hash_key=True,default=''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6)))
    activated = BooleanAttribute(default=False)
    reward_code = UnicodeAttribute(default='BetaTest')


class ServerUserIndex(GlobalSecondaryIndex):
    """
    This class represents a global secondary index
    """
    class Meta:
        read_capacity_units = 1
        write_capacity_units = 1
        # All attributes are projected
        projection = AllProjection()
        index_name = 'user-index'

    # This attribute is the hash key for the index
    # Note that this attribute must also exist
    # in the model
    user = UnicodeAttribute(hash_key=True)

if application.config['STUB_AWS_RESOURCES']:
    ServerUserIndex.Meta.host = 'http://localhost:8000'

class Server(Model):
    """ A game server
    """

    class Meta:
        region = application.config['AWS_REGION']
        table_name = str(application.config['APP_NAME'])+'-servers'

    id = UnicodeAttribute(hash_key=True, default=str(uuid.uuid4()))
    name = UnicodeAttribute(default='Server')
    expiry_date = UTCDateTimeAttribute(default=datetime.datetime.now(timezone.utc)+datetime.timedelta(minutes=65))
    creation_date = UTCDateTimeAttribute(default=datetime.datetime.now(timezone.utc))
    type = UnicodeAttribute(default='ark_server')
    user = UnicodeAttribute()
    user_index = ServerUserIndex()
    size = UnicodeAttribute(default='micro')
    region = UnicodeAttribute()

    userdata = """Content-Type: multipart/mixed; boundary="===============BOUNDARY=="
MIME-Version: 1.0

--===============BOUNDARY==
MIME-Version: 1.0
Content-Type: text/x-shellscript; charset="us-ascii"

#! /bin/bash
ip link set dev eth0 mtu 1460
echo "interface \\"eth0\\" { supersede interface-mtu 1460; }" >> /etc/dhcp/dhclient.conf
echo "fs.file-max=100000" >> /etc/sysctl.conf
echo "session required pam_limits.so" > /etc/pam.d/common-session
echo "msv:password" > /home/ec2-user/users.conf
mkdir -p /mnt/efs/ark/server/ShooterGame/Saved/SavedArks

--===============BOUNDARY==
MIME-Version: 1.0
Content-Type: text/cloud-boothook; charset="us-ascii"

#cloud-boothook
PATH=$PATH:/usr/local/bin
#Instance should be added to an security group that allows HTTP outbound
yum update
#Install jq, a JSON parser
yum -y install jq
#Install NFS client
if ! rpm -qa | grep -qw nfs-utils; then
    yum -y install nfs-utils
fi
if ! rpm -qa | grep -qw python27; then
    yum -y install python27
fi
#Install pip
yum -y install python27-pip
#Install awscli
pip install awscli
#Upgrade to the latest version of the awscli
#pip install --upgrade awscli
#Add support for EFS to the CLI configuration
aws configure set preview.efs true
#Join the ECS cluster
EC2_AVAIL_ZONE=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone`
EC2_INSTANCE_ID=`curl -s http://169.254.169.254/latest/meta-data/instance-id`
EC2_REGION="`echo \"$EC2_AVAIL_ZONE\" | sed -e 's:\([0-9][0-9]*\)[a-z]*\$:\\1:'`"
SERVER_ID="`aws ec2 describe-tags --output text --region $EC2_REGION --filters Name=resource-type,Values="instance" Name=key,Values=Name Name=resource-id,Values=\"$EC2_INSTANCE_ID\"  | cut -f5`"
echo ECS_CLUSTER=$SERVER_ID >> /etc/ecs/ecs.config
echo ECS_ENGINE_TASK_CLEANUP_WAIT_DURATION=30 >> /etc/ecs/ecs.config
echo ECS_IMAGE_CLEANUP_INTERVAL=30 >> /etc/ecs/ecs.config

#Create mount point
mkdir /mnt/efs
#Get EFS FileSystemID attribute
#Instance needs to be added to a EC2 role that give the instance at least read access to EFS
EFS_FILE_SYSTEM_ID=`/usr/local/bin/aws efs describe-file-systems --region $EC2_REGION | jq '.FileSystems[]' | jq 'select(.Name=="ContainerDataFileSystem")' | jq -r '.FileSystemId'`
#Check to see if the variable is set. If not, then exit.
if [-z "$EFS_FILE_SYSTEM_ID"]; then
    echo "ERROR: variable not set" 1> /etc/efssetup.log
    exit
fi
#Instance needs to be a member of security group that allows 2049 inbound/outbound
#The security group that the instance belongs to has to be added to EFS file system configuration
#Create variables for source and target
DIR_SRC=$EC2_AVAIL_ZONE.$EFS_FILE_SYSTEM_ID.efs.$EC2_REGION.amazonaws.com:/
DIR_TGT=/mnt/efs

#Mount EFS file system
mount -t nfs4 $DIR_SRC $DIR_TGT

#make dir for data
mkdir -p /mnt/efs/container_data/$SERVER_ID

umount /mnt/efs

DIR_SRC=$EC2_AVAIL_ZONE.$EFS_FILE_SYSTEM_ID.efs.$EC2_REGION.amazonaws.com:/container_data/$SERVER_ID
DIR_TGT=/mnt/efs

#Mount EFS file system
mount -t nfs4 $DIR_SRC $DIR_TGT

chmod 777 -R /mnt/efs

# set up ark dirs
mkdir -p /mnt/efs/ark/server/ShooterGame/Saved/SavedArks
cd /mnt/efs/ark/
yum -y install wget
wget https://raw.githubusercontent.com/TuRz4m/Ark-docker/master/arkmanager-user.cfg
mv arkmanager-user.cfg arkmanager.cfg
sed -i 's/${SESSIONNAME}/Adventure Servers/g' arkmanager.cfg

#Backup fstab
cp -p /etc/fstab /etc/fstab.back-$(date +%F)
#Append line to fstab
echo -e "$DIR_SRC \t\t $DIR_TGT \t\t nfs \t\t defaults \t\t 0 \t\t 0" | tee -a /etc/fstab
--===============BOUNDARY==--
"""

    prices = {
                'micro': 800,
                'large': 1600
                }

    max_players = {
                    'micro': 20,
                    'large': 80
                    }

    __mapper_args__ = {
                'polymorphic_identity':'server',
                'polymorphic_on':type
            }

    def __init__(self, hash_key=None, range_key=None, **attrs):
        super().__init__(hash_key, range_key, **attrs)
        self.create_cluster()

    def seconds_to_dhms(self):
        if self.expiry_date > datetime.datetime.utcnow().replace(tzinfo=pytz.utc):
            time_remaining = self.expiry_date - datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            days = math.floor(time_remaining.seconds / 86400)
            remainder = time_remaining.seconds % 84600
            hours = math.floor(remainder / 3600)
            remainder %= 60
            minutes = math.floor(remainder / 60)
            return str(days) + " days, " + str(hours) + " hours, " + str(minutes) + " minutes"
        else:
            return "Server expired"

    def serialize(self):
        return {
            "id": str(self.id),
            "expiry_date" : str(self.expiry_date),
            "creation_date": str(self.creation_date),
            "time_remaining": self.seconds_to_dhms(),
            "user": str(self.user),
            "name": str(self.name),
            "status": str(self.status),
            "ip": str(self.ip),
            "size": str(self.size),
            "type": str(self.type)
            #"port": str(self.port)
        }

    def __str__(self):
        return self.id

    @property
    def status(self):
        if application.config['STUB_AWS_RESOURCES']:
            return 'stub_resource'

        client = boto3.client('ecs', region_name=self.region)
        response = client.list_tasks(cluster=self.id)

        instance_status = 'Unknown'

        if (len(response['taskArns']) > 0):
            instance_status = 'Available'

        else:
            instance_status = 'Preparing'

        return instance_status

    @property
    def ip(self):
        client = boto3.client('ec2', region_name=self.region)
        try:
            instance_status =  client.describe_instances(
                InstanceIds=[
                    self.instance_id
                ])['Reservations'][0]['Instances'][0]['PublicIpAddress']
        except:
            instance_status = 'Unknown'

        return instance_status

    @property
    def private_ip(self):
        client = boto3.client('ec2', region_name=self.region)
        try:
            private_ip =  client.describe_instances(
                InstanceIds=[
                    self.instance_id
                ])['Reservations'][0]['Instances'][0]['PrivateIpAddress']
        except:
            private_ip = 'Unknown'

        return private_ip

    def restart(self):
        client = boto3.client('ecs', region_name=self.region)
        taskarn = client.list_tasks(cluster=self.id)['taskArns'][0]
        client.stop_task(cluster=self.id,task=taskarn)

    def apply_promo_code(self,promo_code):

        promo_code_days = {
                'BetaTest': 30,
                '5Days': 5
                }

        promo_code = PromoCode.query.filter_by(code=promo_code).first()

        if promo_code and not promo_code.activated:
            self.expiry_date = self.expiry_date + datetime.timedelta(days=promo_code_days[promo_code.reward_code])

            promo_code.activated=True

            promo_code.save()
            self.save()

    def create_cluster(self):
        try:
            if application.config['STUB_AWS_RESOURCES']:
                return

            # create the ECS cluster
            client = boto3.client('ecs', region_name=self.region)
            if 'MISSING' in str(client.describe_clusters(clusters=[self.id,])):
                try:
                    response = client.create_cluster(
                        clusterName=str(self.id)
                    )
                except IndexError:
                    print('Error describing cluster '+self.id)
                    return
            else:
                return

            client = boto3.client('ec2', region_name=self.region)

            # get the security group
            try:
                security_group_id = client.describe_security_groups(Filters=[{'Name':'tag-key','Values':['Name'],'Name':'tag-value','Values':[self.type+'_sg']}])['SecurityGroups'][0]['GroupId']
            except IndexError:
                print("Error getting the security group for "+self.type+". Has it been created?")

            # get the subnet
            subnet_id = ""
            try:
                subnet_id = client.describe_subnets(Filters=[{'Name':'tag-key','Values':['Name'],'Name':'tag-value','Values':['msv-container-agent-subnet']}])['Subnets'][0]['SubnetId']
            except IndexError:
                print("Error getting the subnet for server. Has it been created?")

            client = boto3.client('ec2', region_name=self.region)

            # create the instance
            response = client.run_instances(
				ImageId=application.config['CONTAINER_AGENT_AMI'][self.region],
				InstanceType='t2.'+str(self.size),
				MinCount = 1,
				MaxCount = 1,
				UserData = str(Server.userdata),
				KeyName = application.config['EC2_KEYPAIR'],
				IamInstanceProfile={
					'Name': application.config['CONTAINER_AGENT_INSTANCE_PROFILE']
					},
				SecurityGroupIds=[security_group_id],
				SubnetId=str(subnet_id),
				BlockDeviceMappings=[
						{
							'DeviceName': '/dev/xvdcz',
							'Ebs': {
								'VolumeSize': 80,
								'DeleteOnTermination': True,
								'VolumeType': 'gp2',
							},
						},
				]
            )
            instance_id = response['Instances'][0]['InstanceId']

            waiter = client.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id,])

            # tag the instance
            response = client.create_tags(
                Resources=[
                    instance_id,
                ],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': self.id
                    },
                    {
                        'Key': 'msv_role',
                        'Value': 'container_agent'
                    },
                ]
            )

            client = boto3.client('autoscaling', region_name=self.region)

            response = client.create_auto_scaling_group(
                AutoScalingGroupName=self.id,
                InstanceId=instance_id,
                MinSize=0,
                MaxSize=1,
                DesiredCapacity=0
            )

            response = client.attach_instances(
                InstanceIds=[
                    instance_id
                ],
                AutoScalingGroupName=self.id
            )

            response = client.update_auto_scaling_group(
                AutoScalingGroupName=self.id,
                MinSize=1,
                MaxSize=1,
                DesiredCapacity=1,
            )

            # create the service
            client = boto3.client('ecs', region_name=self.region)
            client.create_service(
                cluster=self.id,
                serviceName=str(self.type),
                taskDefinition=str(self.type),
                desiredCount=1,
                deploymentConfiguration={
                            'maximumPercent': 100,
                            'minimumHealthyPercent': 0
                        }
            )

        except Exception as e:
            self.delete()
            raise ValueError("Could not create cluster "+self.id+" :"+str(e))

    def delete(self):
        if not application.config['STUB_AWS_RESOURCES']:
            t = Thread(target=self._delete)
            t.start()
        super().delete()

    def _delete(self):

        # terminate the instance if it exists
        client = boto3.client('ec2', region_name=self.region)
        try:
            instance_id = client.describe_instances(Filters=[{'Name':'tag:Name', 'Values':[+self.id]}])['Reservations'][0]['Instances'][0]['InstanceId']
            if len(client.describe_instances(InstanceIds=[instance_id,])['Reservations']) > 0:
                client.terminate_instances(
                        InstanceIds=[
                                    instance_id
                                ]
                )

            # wait to ensure instance terminated
            waiter = client.get_waiter('instance_terminated')
            waiter.wait(
                InstanceIds=[
                            instance_id
                        ],
            )

        except:
            print("Instance not found, moving on")

        # delete the service if it exists
        client = boto3.client('ecs', region_name=self.region)
        services = client.describe_services( cluster=self.id, services=[ self.type ] )['services']
        if len(services) > 0 and services[0]['status'] == 'ACTIVE':
            client.update_service(
                    cluster=self.id,
                    service=str(self.type),
                    desiredCount=0
            )
            client.delete_service(
                    cluster=self.id,
                    service=str(self.type)
            )

        # kill the cluster
        print("Deleting cluster "+self.id)
        client.delete_cluster(
                cluster=self.id
        )

if application.config['STUB_AWS_RESOURCES']:
    Server.Meta.host = 'http://localhost:8000'

def check_if_task_definition_exists(name):
    client = boto3.client('ecs', region_name=application.config['AWS_REGION'])
    response = client.list_task_definitions(
            familyPrefix=name,
    )
    if response['taskDefinitionArns']:
        return True
    return False


