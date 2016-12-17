from mineserve import db
from mineserve.models import Server
import random
import string

class MCPEServer(Server):

    __tablename__ = 'mcpe_server'
    id = db.Column(db.String(255), db.ForeignKey('server.id'), primary_key=True)
    op = db.Column(db.String(255))

    def __init__(self, op, server_name='Adventure Servers', game='mcpe', size='micro'):
        super().__init__(size)

        self.op = op

        self.properties.server_name = server_name

        # random seed
        random.seed(server_name)
        self.properties.level_seed = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(32))

        self.properties.motd = server_name

        self.size=size

        self.game = game

