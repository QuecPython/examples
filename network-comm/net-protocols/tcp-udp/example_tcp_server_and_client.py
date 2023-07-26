import usocket
import _thread
import utime
import checkNet
import dataCall

def _client_conn_proc(conn, ip_addr, port):
    while True:
        try:
            # Receive data sent by the client
            data = conn.recv(1024)
            print('[server] [client addr: %s, %s] recv data:' % (ip_addr, port), data)
            
            # Send data back to the client
            conn.send(data)
        except:
            # Exception occurred and connection closed
            print('[server] [client addr: %s, %s] disconnected' % (ip_addr, port))
            conn.close()
            break

def tcp_server(address, port):
    # Create a socket object
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP_SER)
    print('[server] socket object created.')
    
    # Bind the server IP address and port
    sock.bind((address, port))
    print('[server] bind address: %s, %s' % (address, port))
    
    # Listen for client connection requests
    sock.listen(10)
    print('[server] started, listening ...')
    
    while True:
        # Accept a client connection request
        cli_conn, cli_ip_addr, cli_port = sock.accept()
        print('[server] accept a client: %s, %s' % (cli_ip_addr, cli_port))
        
        # Create a new thread for each client connection for concurrent processing
        _thread.start_new_thread(_client_conn_proc, (cli_conn, cli_ip_addr, cli_port))

def tcp_client(address, port):
    # Create a socket object
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)
    print('[client] socket object created.')
    
    # Connect to the TCP server
    print('[client] connecting: %s, %s' % (address, port))
    sock.connect((address, port))
    print('[client] connected.')
    
    data = b'1234567890'
    while True:
        try:
            # Send data to the server
            sock.send(data)
            print('[client] send data:', data)
            
            # Read the data sent back by the server
            data = sock.recv(1024)
            print('[client] recv data:', data)
            print('[client] -------------------------')
            
            # Delay for 1 second
            utime.sleep(1)
        except:
            # Connection ends until the data is fully received
            print('[client] disconnected.')
            sock.close()
            break

if __name__ == '__main__':
    stage, state = checkNet.waitNetworkReady(30)
    if stage == 3 and state == 1: # Network connection is normal
        print('[net] Network connection successful.')
        
        # Get the IP address of the module
        server_addr = dataCall.getInfo(1, 0)[2][2]
        server_port = 80
        
        # Start the server thread to listen for client connection requests
        _thread.start_new_thread(tcp_server, (server_addr, server_port))
        
        # Delay for a while to ensure that the server starts successfully
        print('sleep 3s to ensure that the server starts successfully.')
        utime.sleep(3)
        
        # Start the client
        tcp_client(server_addr, server_port)
    else:
        print('[net] Network connection failed, stage={}, state={}'.format(stage, state))