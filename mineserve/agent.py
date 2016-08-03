from flask import Flask, request
from docker import Client
import json
app = Flask(__name__)
docker_cli = Client(base_url='unix://var/run/docker.sock')

@app.route('/start', methods=['POST'])
def start():
    for line in docker_cli.pull('itxtech/docker-env-genisys', stream=True):
        print(json.dumps(json.loads(line), indent=4))

    container = docker_cli.create_container(image='itxtech/docker-env-genisys',
                                            ports = ['19133:19132/udp'],
                                            host_config=docker_cli.create_host_config(binds=[
                                                '/home/ubuntu/genisys.phar:/srv/genisys/genisys.phar',
                                                '/home/ubuntu/server.properties:/srv/genisys/server.properties',
                                                ],),
                                            name = 'mcpe',
                                            tty = True,
                                            stdin_open = True,
            )

    response = docker_cli.start(container=container)

    return 'ok'

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
