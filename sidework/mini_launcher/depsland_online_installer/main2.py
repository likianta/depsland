"""
how to use this script:
    import sys
    import subprocess
    conf = {'appid': ..., 'version': ...}
    subprocess.run(
        (sys.executable, __file__, conf['appid'], conf['version'])
    )
"""
print(__name__, __file__)
if __name__ == '__main__':
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'minideps'))

import airmise as air
import webbrowser
from argsense import cli

@cli
def main(
    appid: str, 
    version: str, 
    public_server_host: str = '47.102.108.149'
) -> None:
    """
    params:
        public_server_host:
            default: '47.102.108.149'
            localnet test: '172.20.128.100'
    ref: source code of $[airmise.frp.connect_to_public_transport]
    """
    sock = air.Socket()
    sock.bind('0.0.0.0', 2187)
    sock.connect(public_server_host, 2186)
    
    sock.sendall(air.encode(('register', 2187)))
    type, data = air.decode(sock.recvall())
    assert type == 'connection_established'
    
    public_client_port = data
    print('public port for client: {}'.format(public_client_port))
    webbrowser.open(
        'http://{}:2185/?'
        'client-open-port={}&'
        'target-appid={}&'
        'target-version={}'
        .format(public_server_host, public_client_port, appid, version)
    )
    
    air.util.fix_ctrl_c_keystroke()
    
    slave = air.Slave(sock, {})
    slave.mainloop()

if __name__ == '__main__':
    cli.run(main)
