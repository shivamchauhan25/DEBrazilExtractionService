import os
import socket
import constants

host_ip=socket.gethostbyname(socket.gethostname())
port = constants.APPLICATION_PORT
workers = constants.WORKERS
timeout = constants.TIMEOUT
os.system("gunicorn -w "+ workers + " --threads=4" +" -b " + host_ip + ":" + port + " -t " + timeout +" --reload wsgi:app")