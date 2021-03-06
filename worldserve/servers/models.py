from django.db import models
import uuid
import boto3
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
import datetime


class Server(models.Model):
    id = models.CharField(primary_key=True,
                          max_length=200,
                          default = str(uuid.uuid4()))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    region = models.CharField(max_length=20, default='eu-west-1',
                              choices=[('eu-west-1', 'eu-west-1'),
                                       ('us-east-1', 'us-east-1')])
    server_type = models.CharField(max_length=20,
                                   default='ark',
                                   choices=[('ark', 'Ark: Survival Evolved')])
    expiry_date = models.DateTimeField(default=datetime.datetime.now(datetime.timezone.utc) +
                                       datetime.timedelta(minutes=65))

    def __str__(self):
        return self.id

    @property
    def ip(self):
        client = boto3.client('ec2', region_name=self.region)
        try:
            ip = client.describe_instances(Filters=[{'Name':'tag:Name', 'Values':['wsv-container-'+self.id]}])['Reservations'][0]['Instances'][0]['PublicIpAddress']
        except:
            ip = 'Unknown'
        return ip

    @property
    def status(self):
        client = boto3.client('cloudformation', region_name=self.region)

        response = client.describe_stacks(
            StackName='wsv-server-'+self.id,
        )

        statuses = {
            'CREATE_IN_PROGRESS': 'Setting up',
            'CREATE_COMPLETE': 'Ready'
        }

        status = response['Stacks'][0]['StackStatus']

        if status in statuses:
            return statuses[status]
        else:
            return 'Error'

    def create_stack(self):
        client = boto3.client('cloudformation', region_name=self.region)
        return client.create_stack(
            StackName='wsv-server-'+self.id,
            TemplateBody=open('cloudformation/servers/' +
                              self.server_type + '/server.yaml', 'r').read(),
            Parameters=[
                {
                    'ParameterKey': 'KeyName',
                    'ParameterValue': 'id_rsa'
                },
                {
                    'ParameterKey': 'ServerID',
                    'ParameterValue': str(self.id)
                }
            ],
        )

    def delete_stack(self):
        client = boto3.client('cloudformation', region_name=self.region)
        try:
            response = client.describe_stack_resource(
                StackName='wsv-server-'+self.id,
                LogicalResourceId='AutoScalingGroup'
            )
            autoscalinggroupname = response['StackResourceDetail']['PhysicalResourceId']
            client = boto3.client('autoscaling', region_name=self.region)
            client.delete_auto_scaling_group(
                AutoScalingGroupName=autoscalinggroupname,
                ForceDelete=True
            )

            client = boto3.client('ecs', region_name=self.region)
            services = client.describe_services( cluster=self.id, services=['server'] )['services']
            if len(services) > 0 and services[0]['status'] == 'ACTIVE':
                client.update_service(
                        cluster=self.id,
                        service='server',
                        desiredCount=0
                )
        except:
            pass

        client = boto3.client('cloudformation', region_name='eu-west-1')
        return client.delete_stack(
            StackName='wsv-server-'+self.id,
        )


def initServer(**kwargs):
    if kwargs.get('created') == True:
        instance = kwargs.get('instance')
        instance.create_stack()

def deleteServer(**kwargs):
    instance = kwargs.get('instance')
    instance.delete_stack()


post_save.connect(initServer, Server)
pre_delete.connect(deleteServer, Server)
