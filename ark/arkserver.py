from mineserve import db
from mineserve.models import Server

class ArkServer(Server):

    __tablename__ = 'ark_server'
    id = db.Column(db.String(255), db.ForeignKey('server.id'), primary_key=True)

    __mapper_args__ = {
                'polymorphic_identity':'ark_server',
            }

    def __init__(self, user, size='micro', name='Ark Server'):
        super().__init__(user, size=size, name=name)
        self.connect_port = 7777

    def serialize(self):
        data = super().serialize()
        data['type'] = str(self.type)
        return data
