import socket
from uuid import uuid4

SERVER_HOST = '47.102.108.149'
SERVER_PORT = 2144

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_HOST, SERVER_PORT))

self_id = uuid4().hex
sock.sendall('register={}'.format(self_id).encode())
resp = sock.recv(5)  # a random public port opened for us. e.g. b'31025'
public_port = int(resp)
print('public port: {}'.format(public_port))

# now we are in passive mode.

