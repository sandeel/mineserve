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

    def __init__(self, user, op, name='Adventure Servers', size='micro'):
        super().__init__(user, size)

        self.op = op

        self.properties.server_name = server_name

        # random seed
        random.seed(server_name)
        self.properties.level_seed = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(32))

        self.properties.motd = server_name

        self.size=size

    def serialize(self):
        data = super().serialize()
        data['type'] = str(self.type)
        return data
