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
from flask import Flask, redirect, url_for, request
from sqlalchemy import event
from threading import Thread
from flask_jwt import JWT
from werkzeug.security import safe_str_cmp

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    servers = db.relationship('Server', back_populates='user')

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "servers": [s.id for s in self.servers]
        }


    def __str__(self):
        return self.email

# set up jwt

def authenticate(username, password):
    user = User.query.filter_by(email=username).first()
    if user and verify_password(password, user.password):
        return user

def identity(payload):
    return User.query.filter(User.id == payload['identity']).scalar()

jwt = JWT(application, authenticate, identity)

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


# Customized server admin
class ServerAdmin(ProtectedModelView):
    column_display_pk=True

    column_list = (
        'id',
        'instance_id',
        'status',
        'ip',
        'creation_date',
        'expiry_date',
        'size',
    )

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="servers")
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

    def serialize(self):
        return {
            "id": str(self.id),
            "type": str(self.type),
            "expiry_date" : str(self.expiry_date),
            "creation_date" : str(self.creation_date),
            "user": str(self.user.id),
            "name": str(self.name)
        }

    def __init__(self, user, size='micro', name="New Server"):
        self.id = str(uuid.uuid4())

        self.name = name

        self.size = size

        self.creation_date=datetime.datetime.now()

        # give 1 hour and 5 minutes free
        now = datetime.datetime.now()
        now_plus_1_hours = now + datetime.timedelta(minutes=65)
        self.expiry_date = now_plus_1_hours

        # instantiate default properties
        self.properties = Properties(server_id = self.id)

        self.instance_id = self.create_cluster()

        self.user = user

        db.session.add(self)
        db.session.commit()


    def __str__(self):
        return self.id


    @property
    def status(self):
        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
        try:
            instance_status =  client.describe_instance_status(
                InstanceIds=[
                    self.instance_id
                ])['InstanceStatuses'][0].get('InstanceStatus').get('Status')
        except:
            instance_status = 'Unknown'

        if instance_status == 'ok' and ((datetime.datetime.now() - self.creation_date).seconds < 120):
            instance_status = 'Preparing Genisys'

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

        userdata = """#!/bin/bash

echo ECS_CLUSTER="""+self.id+""" >> /etc/ecs/ecs.config
ip link set dev eth0 mtu 1460
echo "interface \\"eth0\\" { supersede interface-mtu 1460; }" >> /etc/dhcp/dhclient.conf
mkdir /plugins
curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
sudo yum -y install unzip
unzip awscli-bundle.zip
./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws
rm awscli-bundle.zip
/usr/local/bin/aws s3 cp s3://msv-resourcesbucket-1cy9th89fajoy/plugins/pdc.phar /plugins/
/usr/local/bin/aws s3 cp s3://msv-resourcesbucket-1cy9th89fajoy/server.properties /home/ec2-user/
echo "user:password:::upload" > /home/ec2-user/users.conf
        """

        client = boto3.client('ec2', region_name=application.config['AWS_REGION'])

        # get the security group
        try:
            security_group_id = client.describe_security_groups(Filters=[{'Name':'tag-key','Values':['Name'],'Name':'tag-value','Values':[self.type+'_sg']}])['SecurityGroups'][0]['GroupId']
        except IndexError:
            print("Error getting the security group for "+self.type+". Has it been created?")
            return 'fake-instance-id'

        # get the subnet
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
                UserData = userdata,
                KeyName = application.config['EC2_KEYPAIR'],
                IamInstanceProfile={
                    'Name': application.config['CONTAINER_AGENT_INSTANCE_PROFILE']
                    },
                SecurityGroupIds=[security_group_id],
                SubnetId=subnet_id
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
    # if we are in debug don't do anything
    if application.config['STUB_AWS_RESOURCES']:
        print('In stub mode, nothing to do')
        return

    # terminate the instance if it exists
    client = boto3.client('ec2', region_name=application.config['AWS_REGION'])
    if len(client.describe_instances(InstanceIds=[target.instance_id,])['Reservations']) > 0:
        client.terminate_instances(
                InstanceIds=[
                            target.instance_id
                        ]
        )

    # delete the service if it exists
    client = boto3.client('ecs', region_name=application.config['AWS_REGION'])
    if client.describe_services( cluster=target.id, services=[ target.type ] )['services'][0]['status'] == 'ACTIVE':
        client.update_service(
                cluster=target.id,
                service=str(target.type),
                desiredCount=0
        )
        client.delete_service(
                cluster=target.id,
                service=str(target.type)
        )

    # wait to ensure instance shutting down
    time.sleep(10)

    # kill the cluster
    client.delete_cluster(
            cluster=target.id
    )


# Create admin
admin = admin.Admin(application, name='MineServe Admin', template_mode='bootstrap3')
admin.add_view(ServerAdmin(Server,db.session))
admin.add_view(UserAdmin(User,db.session))
admin.add_view(PromoCodeAdmin(PromoCode,db.session))
admin.add_view(ProtectedModelView(Properties,db.session))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(application, user_datastore)

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )

# Executes before the first request is processed.
@application.before_first_request
def before_first_request():

    # Create any database tables that don't exist yet.
    db.create_all()

    # Create the Roles "admin" and "end-user" -- unless they already exist
    user_datastore.find_or_create_role(name='admin', description='Administrator')

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility function to encrypt the password.
    encrypted_password = encrypt_password(application.config['ADMIN_PASSWORD'])
    if not user_datastore.get_user('adventureservers@kolabnow.com'):
        user_datastore.create_user(email='adventureservers@kolabnow.com', password=encrypted_password)

    # Commit any database changes; the User and Roles must exist before we can add a Role to the User
    db.session.commit()

    # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    user_datastore.add_role_to_user('adventureservers@kolabnow.com', 'admin')
    db.session.commit()



