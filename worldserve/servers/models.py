from django.db import models
import uuid
import boto3
from django.db.models.signals import pre_save, pre_delete


class Server(models.Model):
    id = models.CharField(primary_key=True, default=str(uuid.uuid4()), max_length=200)


    def create_stack(self):
        client = boto3.client('cloudformation', region_name='eu-west-1')

        return client.create_stack(
            StackName='server-'+self.id,
            TemplateBody= open('cloudformation/server.yaml', 'r').read(),
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
            StackName='server-'+self.id,
        )


def initServer(**kwargs):
    instance = kwargs.get('instance')
    instance.create_stack()

def deleteServer(**kwargs):
    instance = kwargs.get('instance')
    instance.delete_stack()


pre_save.connect(initServer, Server)
pre_delete.connect(deleteServer, Server)
