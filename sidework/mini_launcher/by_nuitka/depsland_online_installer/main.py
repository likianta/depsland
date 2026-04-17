import airmise as air
import webbrowser

def main():
    """
    ref: source code of $[airmise.frp.connect_to_public_transport]
    """
    # source_port = 2187
    # target_host = '172.20.128.100'
    # target_port = 2186
    
    sock = air.Socket()
    sock.bind('0.0.0.0', 2187)
    sock.connect('172.20.128.100', 2186)
    
    sock.sendall(air.encode(('register', 2187)))
    type, data = air.decode(sock.recvall())
    assert type == 'connection_established'
    
    public_port = data
    print('public port: {}'.format(public_port))
    webbrowser.open(
        'http://172.20.128.100:2185/?client-open-port={}'.format(public_port)
    )
    
    air.util.fix_ctrl_c_keystroke()
    
    slave = air.Slave(sock, {})
    slave.mainloop()

if __name__ == '__main__':
    main()
