from mineserve import db, application
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, current_user, roles_accepted
from flask_security.utils import encrypt_password, verify_password
from flask_admin.contrib import sqla
import flask_admin as admin
import datetime
import uuid
import random
from flask_admin import helpers as admin_helpers
import boto3
import time
import math
from flask import Flask, redirect, url_for, request
from sqlalchemy import event
from threading import Thread

class User():

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

# Create customized model view class
class ProtectedModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

class PromoCode(db.Model):
    code = db.Column(db.String(255), primary_key=True)
    activated = db.Column(db.Boolean)
    reward_code = db.Column(db.String(255))

    def __init__(self, reward_code='BetaTest'):
        self.code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
        self.activated = False
        self.reward_code = reward_code

# Customized promo code admin
class PromoCodeAdmin(ProtectedModelView):
    column_display_pk=True

    form_choices = { 'reward_code': [('BetaTest', 'BetaTest'),
                                     ('5Days', '5Days')],}

# Customized user admin view
class UserAdmin(ProtectedModelView):
    column_display_pk=True

    column_list = (
        'email',
        'active',
    )

class Properties(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.String(255), db.ForeignKey('server.id'))

    #properties
    server_name = db.Column(db.String(255))
    motd = db.Column(db.String(255))
    server_port = db.Column(db.String(255))
    memory_limit= db.Column(db.String(255))
    gamemode = db.Column(db.String(255))
    max_players = db.Column(db.String(255))
    spawn_protection = db.Column(db.String(255))
    level_name = db.Column(db.String(255))
    level_type = db.Column(db.String(255))
    announce_player_achievements = db.Column(db.String(255))
    white_list = db.Column(db.String(255))
    enable_query = db.Column(db.String(255))
    enable_rcon = db.Column(db.String(255))
    allow_flight = db.Column(db.String(255))
    spawn_animals = db.Column(db.String(255))
    spawn_mobs = db.Column(db.String(255))
    force_gamemode = db.Column(db.String(255))
    hardcore = db.Column(db.String(255))
    pvp = db.Column(db.String(255))
    difficulty = db.Column(db.String(255))
    generator_settings = db.Column(db.String(255))
    level_seed = db.Column(db.String(255))
    rcon_password = db.Column(db.String(255))
    auto_save = db.Column(db.String(255))

    def __init__(self, server_id):

        self.server_id = server_id

        # set the default properties
        self.server_name = 'The Server'
        self.motd = 'Adventure Servers Server'
        self.server_port = '33775'
        self.memory_limit = ''
        self.gamemode = '0'
        self.max_players = '60'
        self.spawn_protection = '0'
        self.level_name = 'world'
        self.level_type = 'DEFAULT'
        self.announce_player_achievements = 'on'
        self.white_list = 'off'
        self.enable_query = 'on'
        self.enable_rcon = 'on'
        self.allow_flight = 'off'
        self.spawn_animals = 'on'
        self.spawn_mobs = 'off'
        self.force_gamemode = 'on'
        self.hardcore = 'off'
        self.pvp = 'on'
        self.difficulty = '1'
        self.generator_settings = ''
        self.level_seed = ''
        self.rcon_password = 'password'
        self.auto_save = 'yes'

    def generate_file(self):

        file = ""
        file += 'server-name='+str(self.server_name)+'\n'
        file += 'motd='+str(self.motd)+'\n'
        file += 'server-port='+str(self.server_port)+'\n'
        file += 'memory-limit='+str(self.memory_limit)+'\n'
        file += 'gamemode='+str(self.gamemode)+'\n'
        file += 'max-players='+str(self.max_players)+'\n'
        file += 'spawn-protection='+str(self.spawn_protection)+'\n'
        file += 'level-name='+str(self.level_name)+'\n'
        file += 'level-type='+str(self.level_type)+'\n'
        file += 'announce-player-achievements='+str(self.announce_player_achievements)+'\n'
        file += 'white-list='+str(self.white_list)+'\n'
        file += 'enable-query='+str(self.enable_query)+'\n'
        file += 'enable-rcon='+str(self.enable_rcon)+'\n'
        file += 'allow-flight='+str(self.allow_flight)+'\n'
        file += 'spawn-animals='+str( self.spawn_animals)+'\n'
        file += 'spawn-mobs='+str(self.spawn_mobs)+'\n'
        file += 'force-gamemode='+str(self.force_gamemode)+'\n'
        file += 'hardcore='+str(self.hardcore)+'\n'
        file += 'pvp='+str(self.pvp)+'\n'
        file += 'difficulty='+str(self.difficulty)+'\n'
        file += 'generator-settings='+str(self.generator_settings)+'\n'
        file += 'level-seed='+str(self.level_seed)+'\n'
        file += 'rcon.password='+str(self.rcon_password)+'\n'
        file += 'auto-save='+str(self.auto_save)+'\n'

        return file

class Server(db.Model):

    __tablename__ = 'server'
    id = db.Column(db.String(255), primary_key=True)
    instance_id = db.Column(db.String(255))
    name = db.Column(db.String(255))
    expiry_date = db.Column(db.DateTime)
    creation_date = db.Column(db.DateTime)
    user = db.Column(db.String(255))
    size = db.Column(db.String(255))
    properties = db.relationship("Properties", backref="server", uselist=False)
    type = db.Column(db.String(50))


    sizes = ['micro', 'large']

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

    def seconds_to_dhms(self):
        if self.expiry_date > datetime.datetime.now():
            time_remaining = self.expiry_date - datetime.datetime.now()
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
            "type": str(self.type),
            "expiry_date" : str(self.expiry_date),
            "creation_date": str(self.creation_date),
            "time_remaining": self.seconds_to_dhms(),
            "user": str(self.user),
            "name": str(self.name),
            "status": str(self.status),
            "ip": str(self.ip),
            "port": str(self.port)
        }

    def __init__(self, user, size='micro', name="New Server"):
        self.id = str(uuid.uuid4())

        self._userdata = """#!/bin/bash
echo ECS_CLUSTER="""+str(self.id)+""" >> /etc/ecs/ecs.config
ip link set dev eth0 mtu 1460
echo "interface \\"eth0\\" { supersede interface-mtu 1460; }" >> /etc/dhcp/dhclient.conf
"""

        self.name = name

        self.size = size

        self.creation_date=datetime.datetime.now()

        # give 1 hour and 5 minutes free
        now = datetime.datetime.now()
        now_plus_1_hours = now + datetime.timedelta(minutes=65)
        self.expiry_date = now_plus_1_hours

        # instantiate default properties
        self.properties = Properties(server_id = self.id)

        try:
            self.instance_id = self.create_cluster()
        except Exception as e:
            self.delete_cluster()
            raise ValueError("Could not create cluster "+self.id+" :"+str(e))

        self.user = user

        db.session.add(self)
        db.session.commit()

    @property
    def userdata(self):
        return self._userdata


    def __str__(self):
        return self.id

    @property
    def status(self):
        client = boto3.client('ecs', region_name=application.config['AWS_REGION'])
        response = client.list_tasks(cluster=self.id)

        instance_status = 'Unknown'

        if (len(response['taskArns']) > 0):
            instance_status = 'Available'

        else:
            instance_status = 'Preparing'

        return instance_status

    @property
    def ip(self):
        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
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
        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
        try:
            private_ip =  client.describe_instances(
                InstanceIds=[
                    self.instance_id
                ])['Reservations'][0]['Instances'][0]['PrivateIpAddress']
        except:
            private_ip = 'Unknown'

        return private_ip

    def create_cluster(self):

        if application.config['STUB_AWS_RESOURCES']:
            return 'fake-instance-id'

        # create the ECS cluster
        client = boto3.client('ecs', region_name=application.config['AWS_REGION'])
        response = client.create_cluster(
            clusterName=self.id
        )

        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])

        # get the security group
        try:
            security_group_id = client.describe_security_groups(Filters=[{'Name':'tag-key','Values':['Name'],'Name':'tag-value','Values':[self.type+'_sg']}])['SecurityGroups'][0]['GroupId']
        except IndexError:
            print("Error getting the security group for "+self.type+". Has it been created?")
            return 'fake-instance-id'

        # get the subnet
        subnet_id = ""
        try:
            subnet_id = client.describe_subnets(Filters=[{'Name':'tag-key','Values':['Name'],'Name':'tag-value','Values':['PublicSubnet1']}])['Subnets'][0]['SubnetId']
        except IndexError:
            print("Error getting the subnet for server. Has it been created?")
            return 'fake-instance-id'

        # create the instance
        response = client.run_instances(
                ImageId=application.config['CONTAINER_AGENT_AMI'],
                InstanceType='t2.'+str(self.size),
                MinCount = 1,
                MaxCount = 1,
                UserData = self.userdata,
                KeyName = application.config['EC2_KEYPAIR'],
                IamInstanceProfile={
                    'Name': application.config['CONTAINER_AGENT_INSTANCE_PROFILE']
                    },
                SecurityGroupIds=[security_group_id],
                SubnetId=str(subnet_id)
        )
        instance_id = response['Instances'][0]['InstanceId']

        time.sleep(1)


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
                    'Key': 'mineserv_role',
                    'Value': 'container_agent'
                },
            ]
        )

        # create the service
        client = boto3.client('ecs', region_name=application.config['AWS_REGION'])
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

        return instance_id

    def delete_cluster(self):
        t = Thread(target=self._delete_cluster)
        t.start()

    def _delete_cluster(self):

        # terminate the instance if it exists
        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
        try:
            instance_id = client.describe_instances(Filters=[{'Name':'tag:Name', 'Values':[self.id]}])['Reservations'][0]['Instances'][0]['InstanceId']
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
        client = boto3.client('ecs', region_name=application.config['AWS_REGION'])
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


    def restart(self):
        client = boto3.client('ecs', region_name=application.config['AWS_REGION'])
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
            db.session.add(self)

            promo_code.activated=True
            db.session.add(promo_code)

            db.session.commit()

    def reboot_instance(self):
        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
        response = client.reboot_instances(
            InstanceIds=[
                self.instance_id,
            ]
        )
        return response

def check_if_task_definition_exists(name):
    client = boto3.client('ecs', region_name=application.config['AWS_REGION'])
    response = client.list_task_definitions(
            familyPrefix=name,
    )
    if response['taskDefinitionArns']:
        return True
    return False

@event.listens_for(Server, 'before_delete', propagate=True)
def receive_before_delete(mapper, connection, target):
    target.delete_cluster()

# Create admin
admin = admin.Admin(application, name='MineServe Admin', template_mode='bootstrap3')
admin.add_view(PromoCodeAdmin(PromoCode,db.session))
admin.add_view(ProtectedModelView(Properties,db.session))

# Executes before the first request is processed.
@application.before_first_request
def before_first_request():

    # Create any database tables that don't exist yet.
    db.create_all()

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility function to encrypt the password.
    #encrypted_password = encrypt_password(application.config['ADMIN_PASSWORD'])
    #if not user_datastore.get_user('adventureservers@kolabnow.com'):
        #user_datastore.create_user(email='adventureservers@kolabnow.com', password=encrypted_password)

    # Commit any database changes; the User and Roles must exist before we can add a Role to the User
    #db.session.commit()

    # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    #user_datastore.add_role_to_user('adventureservers@kolabnow.com', 'admin')
    db.session.commit()



