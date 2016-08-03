from application import application
from application import db

@application.route("/ark", methods=["GET"])
def ark():
    return render_template('servers.html', servers = current_user.servers)

class ArkServer(db.Model):

    __tablename__ = 'arkserver'
    id = db.Column(db.String(255), primary_key=True)

    def __init__(self):
        print('2hellp')
