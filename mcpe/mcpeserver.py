from mineserve import db
from mineserve.models import Server
import random
import string

class MCPEServer(Server):

    __tablename__ = 'mcpe_server'
    id = db.Column(db.String(255), db.ForeignKey('server.id'), primary_key=True)
    op = db.Column(db.String(255))

    __mapper_args__ = {
                'polymorphic_identity':'mcpe_server',
            }

    connect_port = 19132

    def __init__(self, user, name='Adventure Servers', size='micro'):
        super().__init__(user, size)

        self.properties.server_name = name

        # random seed
        random.seed(name)
        self.properties.level_seed = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(32))

        self.properties.motd = name

        self.size=size

    def serialize(self):
        data = super().serialize()
        data['type'] = str(self.type)
        return data

    @property
    def userdata(self):
        return self._userdata + """echo "user:password:::upload" > /home/ec2-user/users.conf
"""
