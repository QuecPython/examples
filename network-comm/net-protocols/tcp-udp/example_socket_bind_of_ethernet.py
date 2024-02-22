# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#     http://www.apache.org/licenses/LICENSE-2.0
#  
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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