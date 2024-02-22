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

import usocket
import _thread
import utime
import checkNet
import dataCall

def udp_server(address, port):
    # Create a socket object
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM, usocket.IPPROTO_UDP)
    print('[server] socket object created.')
    
    # Bind server IP address and port
    sock.bind((address, port))
    print('[server] bind address: %s, %s' % (address, port))
    
    while True:
        # Read client data
        data, sockaddr = sock.recvfrom(1024)
        print('[server] [client addr: %s] recv data: %s' % (sockaddr, data))
        
        # Send data back to the client
        sock.sendto(data, sockaddr)

def udp_client(address, port):
    # Create a socket object
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM, usocket.IPPROTO_UDP)
    print('[client] socket object created.')
    
    data = b'1234567890'
    while True:
        # Send data to the server
        sock.sendto(data, (address, port))
        print('[client] send data:', data)
        
        # Read data sent back from the server
        data, sockaddr = sock.recvfrom(1024)
        print('[client] [server addr: %s] recv data: %s' % (sockaddr, data))
        print('[client] -------------------------')
        
        # Delay for 1 second
        utime.sleep(1)
        
if __name__ == '__main__':
    stage, state = checkNet.waitNetworkReady(30)
    if stage == 3 and state == 1: # Network connection is normal
        print('[net] Network connection successful.')
        
        # Get the IP address of the module
        server_addr = dataCall.getInfo(1, 0)[2][2]
        server_port = 80
        
        # Start the server thread
        _thread.start_new_thread(udp_server, (server_addr, server_port))
        
        # Delay for a while to ensure that the server starts successfully
        print('sleep 3s to ensure that the server starts successfully.')
        utime.sleep(3)
        
        # Start the client
        udp_client(server_addr, server_port)
    else:
        print('[net] Network connection failed, stage={}, state={}'.format(stage, state))