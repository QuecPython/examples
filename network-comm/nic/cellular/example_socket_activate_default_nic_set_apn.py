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

import checkNet
import usocket
import dataCall
from misc import Power

# Configure the APN information according to your actual needs
usrCfg = {'apn': '3gnet', 'username': '', 'password': ''}


def checkAPN():
    # Get the APN information of the first cellular NIC and check if the current one is the one you specified
    pdpCtx = dataCall.getPDPContext(1)
    if pdpCtx != -1:
        if pdpCtx[1] != usrCfg['apn']:
            # If it is not the APN you need, configure it as follows
            ret = dataCall.setPDPContext(1, 0, usrCfg['apn'], usrCfg['username'], usrCfg['password'], 0)
            if ret == 0:
                print('APN configuration successful. Ready to restart to make APN take effect.')
                print('Please re-execute this program after restarting.')
                # Make a data call according to the configured information after the module reboots
                Power.powerRestart()
            else:
                print('APN configuration failed.')
                return False
        else:
            print('The APN is correct and no configuration is required')
            return True
    else:
        print('Failed to get PDP Context.')
        return False


def main():
    checkpass = checkAPN()
    if not checkpass:
        return

    stage, state = checkNet.waitNetworkReady(20)
    if stage == 3 and state == 1:
        print('Network connected successfully.')
        # Create a socket object
        sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        # Resolve the domain name
        try:
            sockaddr = usocket.getaddrinfo('python.quectel.com', 80)[0][-1]
        except Exception:
            print('Domain name resolution failed.')
            sock.close()
            return
        # Connect to the server
        sock.connect(sockaddr)
        # Send data to the server
        ret = sock.send('GET /News HTTP/1.1\r\nHost: python.quectel.com\r\nAccept-Encoding: deflate\r\nConnection: keep-alive\r\n\r\n')
        print('send {} bytes'.format(ret))

        # Receive data from the server
        data = sock.recv(256)
        print('recv {} bytes:'.format(len(data)))
        print(data.decode())

        # Close the connection
        sock.close()
    else:
        print('Network connected failed, stage={}, state={}'.format(stage, state))


if __name__ == '__main__':
    main()
