from mineserve import db
from mineserve.models import Server

class FactorioServer(Server):

    __tablename__ = 'factorio_server'
    id = db.Column(db.String(255), db.ForeignKey('server.id'), primary_key=True)
    op = db.Column(db.String(255))

    __mapper_args__ = {
                'polymorphic_identity':'factorio_server',
            }

    connect_port = 34197

    def __init__(self, user, name, size='micro'):
        super().__init__(name=name, size=size, user=user)

    def serialize(self):
        data = super().serialize()
        data['type'] = str(self.type)
        return data

    @property
    def userdata(self):
        return self._userdata + """echo "msv:password:::" > /home/ec2-user/users.conf
mkdir /home/ec2-user/factorio
mkdir /home/ec2-user/factorio/mods
mkdir /home/ec2-user/factorio/saves
chmod 777 -R /home/ec2-user/factorio
"""
