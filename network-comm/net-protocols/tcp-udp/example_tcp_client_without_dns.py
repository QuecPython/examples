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