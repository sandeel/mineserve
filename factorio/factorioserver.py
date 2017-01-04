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
        self.server_settings ="""{
  "name": "Name of the game as it will appear in the game listing",
  "description": "Description of the game that will appear in the listing",
  "tags": ["game", "tags"],

  "_comment_max_players": "Maximum number of players allowed, admins can join even a full server. 0 means unlimited.",
  "max_players": 0,

  "_comment_visibility": ["public: Game will be published on the official Factorio matching server",
                          "lan: Game will be broadcast on LAN"],
  "visibility":
  {
    "public": true,
    "lan": true
  },

  "_comment_credentials": "Your factorio.com login credentials. Required for games with visibility public",
  "username": "",
  "password": "",

  "_comment_token": "Authentication token. May be used instead of 'password' above.",
  "token": "",

  "game_password": "",

  "_comment_require_user_verification": "When set to true, the server will only allow clients that have a valid Factorio.com account",
  "require_user_verification": false,

  "_comment_max_upload_in_kilobytes_per_second" : "optional, default value is 0. 0 means unlimited.",
  "max_upload_in_kilobytes_per_second": 0,

  "_comment_minimum_latency_in_ticks": "optional one tick is 16ms in default speed, default value is 0. 0 means no minimum.",
  "minimum_latency_in_ticks": 0,

  "_comment_ignore_player_limit_for_returning_players": "Players that played on this map already can join even when the max player limit was reached.",
  "ignore_player_limit_for_returning_players": false,

  "_comment_allow_commands": "possible values are, true, false and admins-only",
  "allow_commands": "admins-only",

  "_comment_autosave_interval": "Autosave interval in minutes",
  "autosave_interval": 10,

  "_comment_autosave_slots": "server autosave slots, it is cycled through when the server autosaves.",
  "autosave_slots": 5,

  "_comment_afk_autokick_interval": "How many minutes until someone is kicked when doing nothing, 0 for never.",
  "afk_autokick_interval": 0,

  "_comment_auto_pause": "Whether should the server be paused when no players are present.",
  "auto_pause": true,

  "only_admins_can_pause_the_game": true,

  "_comment_autosave_only_on_server": "Whether autosaves should be saved only on server or also on all connected clients. Default is true.",
  "autosave_only_on_server": true,

  "_comment_admins": "List of case insensitive usernames, that will be promoted immediately",
  "admins": []
}"""
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
mkdir /home/ec2-user/factorio/data
chmod 777 -R /home/ec2-user/factorio
echo '"""+self.server_settings+"""' > /home/ec2-user/factorio/data/server-settings.json
"""
