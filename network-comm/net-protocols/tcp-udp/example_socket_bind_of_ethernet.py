import ethernet
import usocket

# Create an Ethernet NIC
eth = ethernet.W5500(b'\x12\x34\x56\x78\x9a\xbc','','','',-1,38,36,37, 0)
print('W5500 ethernet nic created.')

# Enable DHCP
eth.dhcp()
print('DHCP enabled.')

# Enable NIC
eth.set_up()
print('Ethernet nic enabled.')

# After the NIC is registered, check the network configuration information
ip_conf = eth.ipconfig()
print('get ip_conf:', ip_conf)

def tcp_client(address, port):
    # Create a socket object
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)
    print('socket object created.')
	
    # Bind the Ethernet NIC IP address after creating the socket object and before connecting to the server
    local_address = ip_conf[1][1]
    sock.bind((local_address, 0))
    print('bind ethernet address: %s', local_address)
	
    # Resolve the domain name
    sockaddr=usocket.getaddrinfo(address, port)[0][-1]
    print('DNS for %s: %s' % (address, sockaddr[0]))
    
    # Connect to the TCP server
    sock.connect(sockaddr)
    print('tcp link established.')
    
    # More code in TCP client samples above