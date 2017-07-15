from django.db import models
import uuid
import boto3
from django.db.models.signals import pre_save, pre_delete
from django.contrib.auth.models import User


class Server(models.Model):
    id = models.CharField(primary_key=True,
                          default=str(uuid.uuid4()),
                          max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    region = models.CharField(max_length=20, default='eu-west-1',
                              choices=[('eu-west-1', 'eu-west-1'),
                                       ('us-east-1', 'us-east-1')])
    server_type = models.CharField(max_length=20,
                                   default='ark',
                                   choices=[('ark', 'ark')])

    @property
    def ip(self):
        client = boto3.client('ec2', region_name=self.region)
        try:
            ip = client.describe_instances(Filters=[{'Name':'tag:Name', 'Values':['wsv-'+self.id]}])['Reservations'][0]['Instances'][0]['PublicIpAddress']
        except:
            ip = 'Unknown'
        return ip

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
        client = boto3.client('cloudformation', region_name='eu-west-1')

        return client.delete_stack(
            StackName='wsv-server-'+self.id,
        )


def initServer(**kwargs):
    instance = kwargs.get('instance')
    instance.create_stack()

def deleteServer(**kwargs):
    instance = kwargs.get('instance')
    instance.delete_stack()


pre_save.connect(initServer, Server)
pre_delete.connect(deleteServer, Server)
