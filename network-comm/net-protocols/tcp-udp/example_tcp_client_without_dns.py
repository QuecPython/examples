import usocket
import checkNet

def tcp_client(address, port):
    # Create a socket object
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)
    print('socket object created.')
    
    # Connect to the TCP server
    sock.connect((address, port))
    print('tcp link established: %s, %s' % (address, port))
    
    # Package user data
    data = 'GET / HTTP/1.1\r\n'
    data += 'Host: ' + address + ':' + str(port) + '\r\n'
    data += 'Connection: close\r\n'
    data += '\r\n'
    data = data.encode()
    
    # Send the data
    sock.send(data)
    print('<-- send data:')
    print(data)
    
    # Receive the data
    print('--> recv data:')
    while True:
        try:
            data = sock.recv(1024)
            print(data)
        except:
            # Connection ends until the data is fully received
            print('tcp disconnected.')
            sock.close()
            break

if __name__ == '__main__':
    stage, state = checkNet.waitNetworkReady(30)
    if stage == 3 and state == 1: # Network connection is normal
        print('Network connection successful.')
        tcp_client('36.152.44.95', 80) # Start the client
    else:
        print('Network connection failed, stage={}, state={}'.format(stage, state))