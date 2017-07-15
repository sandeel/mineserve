from mineserve import application
from datetime import timezone
from datetime import datetime
from datetime import timedelta
import uuid
import random
import boto3
import time
import math
from threading import Thread
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, \
    UTCDateTimeAttribute
import string
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
import pytz


class User():
    """ User of site (Cognito)
    """

    def __init__(self, username):
        client = boto3.client('cognito-idp',
                              region_name=application.config['AWS_REGION'])

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


topup_packages = {
    "normal30days": {
        "days": 30,
        "charge": 3000
    }
}


class PromoCode(Model):
    """ Promo Code for the site
    Can have various uses including free top-up time
    """
    class Meta:
        region = application.config['AWS_REGION']
        table_name = str(application.config['APP_NAME'])+'-promocodes'

    code = UnicodeAttribute(hash_key=True)
    activated = BooleanAttribute(default=False)
    topup_package = UnicodeAttribute(default='normal30days')

    def __init__(self):
        code = ''.join(random.SystemRandom()
                       .choice(string.ascii_uppercase + string.digits)
                       for _ in range(6))
        self.code = code


class ServerUserIndex(GlobalSecondaryIndex):
    """
    This class represents a global secondary index for DynamodDB
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
    expiry_date = UTCDateTimeAttribute(default=datetime.now(timezone.utc) +
                                       timedelta(minutes=65))
    creation_date = UTCDateTimeAttribute(default=datetime.now(timezone.utc))
    type = UnicodeAttribute(default='ark_server')
    user = UnicodeAttribute()
    user_index = ServerUserIndex()
    size = UnicodeAttribute(default='micro')
    region = UnicodeAttribute()
    password = UnicodeAttribute()

    def __init__(self, hash_key=None, range_key=None, **attrs):
        super().__init__(hash_key, range_key, **attrs)
        self.password = self.generate_random_password()
        self.create_stack()

    def generate_random_password(self):
        password = ''.join(random.SystemRandom().
                           choice(string.ascii_uppercase + string.digits)
                           for _ in range(6))
        return password

    @property
    def userdata(self):
        userdata="""Content-Type: multipart/mixed; boundary="===============BOUNDARY=="
MIME-Version: 1.0

--===============BOUNDARY==
MIME-Version: 1.0
Content-Type: text/x-shellscript; charset="us-ascii"

#! /bin/bash
ip link set dev eth0 mtu 1460
echo "interface \\"eth0\\" { supersede interface-mtu 1460; }" >> /etc/dhcp/dhclient.conf
echo "fs.file-max=100000" >> /etc/sysctl.conf
echo "session required pam_limits.so" > /etc/pam.d/common-session
echo "msv:"""+self.password+"""" > /home/ec2-user/users.conf
mkdir -p /mnt/efs/ark/server/ShooterGame/Saved/SavedArks

--===============BOUNDARY==
MIME-Version: 1.0
Content-Type: text/cloud-boothook; charset="us-ascii"

#cloud-boothook
PATH=$PATH:/usr/local/bin
cloud-init-per once docker_options echo 'OPTIONS="${OPTIONS} --storage-opt dm.basesize=80G"' >> /etc/sysconfig/docker
yum -y update
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
SERVER_ID="""+self.id+"""
echo ECS_CLUSTER=$SERVER_ID >> /etc/ecs/ecs.config
echo ECS_ENGINE_TASK_CLEANUP_WAIT_DURATION=30 >> /etc/ecs/ecs.config
echo ECS_IMAGE_CLEANUP_INTERVAL=30 >> /etc/ecs/ecs.config

aws ec2 create-tags --region $EC2_REGION --resources $EC2_INSTANCE_ID --tags Key=Name,Value=msv-container-$SERVER_ID

#Create mount point
mkdir /mnt/efs
mkdir /mnt/clusters
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
mkdir -p /mnt/efs/clusters

umount /mnt/efs

# saved data
DIR_SRC=$EC2_AVAIL_ZONE.$EFS_FILE_SYSTEM_ID.efs.$EC2_REGION.amazonaws.com:/container_data/$SERVER_ID
DIR_TGT=/mnt/efs
mount -t nfs4 $DIR_SRC $DIR_TGT


# clusters
DIR_SRC=$EC2_AVAIL_ZONE.$EFS_FILE_SYSTEM_ID.efs.$EC2_REGION.amazonaws.com:/clusters
DIR_TGT=/mnt/clusters
mount -t nfs4 $DIR_SRC $DIR_TGT

chmod 777 -R /mnt/efs
chmod 777 -R /mnt/clusters

# set up ark dirs
mkdir -p /mnt/efs/ark/server/ShooterGame/Saved/SavedArks
cd /mnt/efs/ark/
yum -y install wget
wget https://raw.githubusercontent.com/TuRz4m/Ark-docker/master/arkmanager-user.cfg
cat > arkmanager_new.cfg << EOF
# --- USER CONFIG --- #
# ARK server options - use ark_<optionname>=<value>
# comment out these values if you want to define them
# inside your GameUserSettings.ini file
serverMap="TheIsland"                                          # server map (default TheIsland)
#serverMapModId="469987622"                                         # Uncomment this to specify the Map Mod Id (<fileid> in http://steamcommunity.com/sharedfiles/filedetails/?id=<fileid>)
#ark_TotalConversionMod="496735411"                                 # Uncomment this to specify a total-conversion mod
ark_SessionName="$SERVER_ID"                                  # if your session name needs special characters please use the .ini instead
ark_ServerPassword=                            # ARK server password, empty: no password required to login
ark_ServerAdminPassword="""+self.password+"""                        # ARK server admin password, KEEP IT SAFE!
ark_MaxPlayers=100                                      # Number MAX of player
# ark_bRawSockets=""                                            # Uncomment if you want to use ark raw socket (instead of steam p2p) [Not recommended]
arkflag_log=""


# ----- Mods ----- #
#ark_GameModIds="487516323,487516324,487516325"                     # Uncomment to specify additional mods by Mod Id separated by commas
# Mod OS Selection
mod_branch=Windows
# Add mod-specific OS selection below:
#mod_branch_496735411=Windows
# ----------------#

# ARK server flags - use arkflag_<optionname>=true
#arkflag_OnlyAdminRejoinAsSpectator=true                            # Uncomment to only allow admins to rejoin as spectator
#arkflag_DisableDeathSpectator=true                                 # Uncomment to disable players from becoming spectators when they die


# ark cluster settings
arkflag_NoTransferFromFiltering=""
arkopt_clusterid=$SERVER_ID
arkopt_ClusterDirOverride=/ark/clusters

# ARK server options - i.e. for -optname=val, use arkopt_optname=val
#arkopt_StructureDestructionTag=DestroySwampSnowStructures

#ark_AltSaveDirectoryName="SotF"                                    # Uncomment to specify a different save directory name

# Update warning messages
# Modify as desired, putting the %d replacement operator where the number belongs
msgWarnUpdateMinutes="This ARK server will shutdown for an update in %d minutes"
msgWarnUpdateSeconds="This ARK server will shutdown for an update in %d seconds"
msgWarnRestartMinutes="This ARK server will shutdown for a restart in %d minutes"
msgWarnRestartSeconds="This ARK server will shutdown for a restart in %d seconds"
msgWarnShutdownMinutes="This ARK server will shutdown in %d minutes"
msgWarnShutdownSeconds="This ARK server will shutdown in %d seconds"

# config environment
arkwarnminutes="60"                                                 # number of minutes to warn players when using update --warn
arkBackupPreUpdate="false"                                          # set this to true if you want to perform a backup before updating

# Options to automatically remove old backups to keep backup size in check
# Each compressed backup is generally about 1-2MB in size.
arkMaxBackupSizeMB="500"                                            # Set to automatically remove old backups when size exceeds this limit
#arkMaxBackupSizeGB="2"                                             # Uncomment this and comment the above to specify the limit in whole GB
EOF
[ ! -f arkmanager.cfg ] && mv arkmanager_new.cfg arkmanager.cfg

cat > GameUserSettings_new.ini << EOF
[ServerSettings]
ServerCrosshair=True
ServerPassword=
ServerAdminPassword="""+self.password+"""
RCONEnabled=True
RCONPort=32330
TheMaxStructuresInRange=10500.000000
OxygenSwimSpeedStatMultiplier=1.000000
StructurePreventResourceRadiusMultiplier=1.000000
RaidDinoCharacterFoodDrainMultiplier=1.000000
PvEDinoDecayPeriodMultiplier=1.000000
KickIdlePlayersPeriod=3600.000000
PerPlatformMaxStructuresMultiplier=1.000000
AutoSavePeriodMinutes=30.000000
ListenServerTetherDistanceMultiplier=1.000000
MaxTamedDinos=5000.000000
RCONServerGameLogBuffer=600.000000
AllowHitMarkers=True

[/Script/ShooterGame.ShooterGameUserSettings]
MasterAudioVolume=1.000000
MusicAudioVolume=1.000000
SFXAudioVolume=1.000000
VoiceAudioVolume=1.000000
UIScaling=1.000000
UIQuickbarScaling=1.000000
CameraShakeScale=1.000000
bFirstPersonRiding=False
bThirdPersonPlayer=False
bShowStatusNotificationMessages=True
TrueSkyQuality=0.000000
FOVMultiplier=1.000000
GroundClutterDensity=0.000000
bFilmGrain=False
bMotionBlur=False
bUseDFAO=False
bUseSSAO=False
bShowChatBox=True
bCameraViewBob=True
bInvertLookY=False
bFloatingNames=True
bChatBubbles=True
bHideServerInfo=False
bJoinNotifications=False
bCraftablesShowAllItems=False
bLocalInventoryItemsShowAllItems=False
bLocalInventoryCraftingShowAllItems=False
bRemoteInventoryItemsShowAllItems=False
bRemoteInventoryCraftingShowAllItems=False
bRemoteInventoryShowEngrams=True
LookLeftRightSensitivity=1.000000
LookUpDownSensitivity=1.000000
GraphicsQuality=1
ActiveLingeringWorldTiles=1
ClientNetQuality=3
LastServerSearchType=0
LastDLCTypeSearchType=-1
LastServerSearchHideFull=False
LastServerSearchProtected=False
HideItemTextOverlay=True
bDistanceFieldShadowing=False
LODScalar=0.780000
bToggleToTalk=False
HighQualityMaterials=True
HighQualitySurfaces=True
bTemperatureF=False
bDisableTorporEffect=False
bChatShowSteamName=False
bChatShowTribeName=True
EmoteKeyBind1=0
EmoteKeyBind2=0
bNoBloodEffects=False
bLowQualityVFX=False
bSpectatorManualFloatingNames=False
bSuppressAdminIcon=False
bUseSimpleDistanceMovement=False
bDisableMeleeCameraSwingAnims=False
bHighQualityAnisotropicFiltering=False
bUseLowQualityLevelStreaming=True
bPreventInventoryOpeningSounds=False
bPreventItemCraftingSounds=False
bPreventHitMarkers=False
bPreventCrosshair=False
bPreventColorizedItemNames=False
bHighQualityLODs=False
bExtraLevelStreamingDistance=False
bEnableColorGrading=True
DOFSettingInterpTime=0.000000
bDisableBloom=False
bDisableLightShafts=False
bDisableMenuTransitions=False
bEnableInventoryItemTooltips=True
bRemoteInventoryShowCraftables=False
LocalItemSortType=0
LocalCraftingSortType=0
RemoteItemSortType=0
RemoteCraftingSortType=0
LastPVESearchType=-1
VersionMetaTag=1
bUseVSync=False
MacroCtrl0=
MacroCtrl1=
MacroCtrl2=
MacroCtrl3=
MacroCtrl4=
MacroCtrl5=
MacroCtrl6=
MacroCtrl7=
MacroCtrl8=
MacroCtrl9=
ResolutionSizeX=1280
ResolutionSizeY=720
LastUserConfirmedResolutionSizeX=1280
LastUserConfirmedResolutionSizeY=720
WindowPosX=-1
WindowPosY=-1
bUseDesktopResolutionForFullscreen=False
FullscreenMode=2
LastConfirmedFullscreenMode=2
Version=5

[ScalabilityGroups]
sg.ResolutionQuality=100
sg.ViewDistanceQuality=3
sg.AntiAliasingQuality=3
sg.ShadowQuality=3
sg.PostProcessQuality=3
sg.TextureQuality=3
sg.EffectsQuality=3
sg.TrueSkyQuality=3
sg.GroundClutterQuality=3
sg.IBLQuality=1
sg.HeightFieldShadowQuality=3
sg.GroundClutterRadius=10000

[SessionSettings]
SessionName=$SERVER_ID

[/Script/Engine.GameSession]
MaxPlayers=70
EOF

[ ! -f GameUserSettings.ini ] && mv GameUserSettings_new.ini GameUserSettings.ini
[ ! -f Game.ini ] && touch Game.ini
[ ! -f AllowedCheaterSteamIDs.txt ] && touch AllowedCheaterSteamIDs.txt

sed -i 's/${SESSIONNAME}/"""+self.id+"""/g' arkmanager.cfg

#Backup fstab
cp -p /etc/fstab /etc/fstab.back-$(date +%F)
#Append line to fstab
echo -e "$DIR_SRC \t\t $DIR_TGT \t\t nfs \t\t defaults \t\t 0 \t\t 0" | tee -a /etc/fstab
--===============BOUNDARY==--
"""
        return userdata

    def seconds_to_dhms(self):
        if self.expiry_date > datetime.utcnow().replace(tzinfo=pytz.utc):
            time_remaining = (self.expiry_date -
                              datetime.utcnow().replace(tzinfo=pytz.utc))
            days = math.floor(time_remaining.seconds / 86400)
            remainder = time_remaining.seconds % 84600
            hours = math.floor(remainder / 3600)
            remainder %= 60
            minutes = math.floor(remainder / 60)
            return (str(days) + " days, " +
                    str(hours) + " hours, " +
                    str(minutes) + " minutes")
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
            "type": str(self.type),
            "port": "27015",
            "password": str(self.password)
        }

    def __str__(self):
        return self.id

    @property
    def status(self):
        if application.config['STUB_AWS_RESOURCES']:
            return 'stub_resource'

        instance_status = 'Unknown'

        client = boto3.client('ecs', region_name=self.region)

        response = client.list_tasks(cluster=self.id)

        if (len(response['taskArns']) > 0):
            taskarn = response['taskArns'][0]

            response = client.describe_tasks(cluster=self.id, tasks=[taskarn,])

            if (str(response['tasks'][0]['lastStatus']) == 'RUNNING'):
                instance_status = 'Available'
            else:
                instance_status = 'Preparing'

        return instance_status

    @property
    def ip(self):
        client = boto3.client('ec2', region_name=self.region)
        try:
            ip = client.describe_instances(Filters=[{'Name':'tag:Name', 'Values':['msv-container-'+self.id]}])['Reservations'][0]['Instances'][0]['PublicIpAddress']
        except:
            ip = 'Unknown'

        return ip

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
            self.expiry_date = self.expiry_date + timedelta(days=topup_packages[str(promo_code.topup_package)]['days'])

            promo_code.activated=True

            promo_code.save()
            self.save()

    def create_stack(self):
        try:
            client = boto3.client('cloudformation')

            client.create_stack(
                StackName=self.id,
                TemplateBody= open('cloudformation/server.yaml', 'r').read(),
				Parameters=[
					{
						'KeyName': 'id_rsa',
						'ServerID': self.id,
					},
				],
            )

            """
            # create the ECS cluster
            client = boto3.client('ecs', region_name=self.region)
            if 'MISSING' in str(client.describe_clusters(clusters=[self.id,])):
                try:
                    response = client.create_stack(
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


            # create the launch config
            client = boto3.client('autoscaling', region_name=self.region)
            response = client.create_launch_configuration(
                ImageId=application.config['CONTAINER_AGENT_AMI'][self.region],
                LaunchConfigurationName=str(self.id),
                InstanceType='t2.'+str(self.size),
                UserData = str(self.userdata),
                KeyName = application.config['EC2_KEYPAIR'],
                IamInstanceProfile=application.config['CONTAINER_AGENT_INSTANCE_PROFILE'],
                SecurityGroups=[security_group_id],
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

            client = boto3.client('autoscaling', region_name=self.region)

            response = client.create_auto_scaling_group(
                AutoScalingGroupName=str(self.id),
                LaunchConfigurationName=str(self.id),
                MinSize=1,
                MaxSize=1,
                DesiredCapacity=1,
                VPCZoneIdentifier=str(subnet_id)
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
        """

        except Exception as e:
            self.delete()
            raise ValueError("Could not create cluster "+self.id+" :"+str(e))

    def delete(self):
        if not application.config['STUB_AWS_RESOURCES']:
            t = Thread(target=self._delete)
            t.start()
        super().delete()

    @property
    def instance_id(self):
        instance_id = client.describe_instances(Filters=[{'Name':'tag:Name', 'Values':[+self.id]}])['Reservations'][0]['Instances'][0]['InstanceId']
        return instance_id

    def _delete(self):

        client = boto3.client('autoscaling', region_name=self.region)

        try:
            response = client.delete_auto_scaling_group(
                AutoScalingGroupName=self.id,
                ForceDelete=True
            )
        except:
            print("ASG not found, moving on")

        time.sleep(60)

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


