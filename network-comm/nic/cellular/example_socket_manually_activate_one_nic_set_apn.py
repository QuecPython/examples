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
import utime
from misc import Power

# Configure the APN information according to your actual needs
usrCfg1 = {'profileID': 1, 'apn': '3gnet', 'username': '', 'password': ''}

'''
Environment configuration:
1. Disable the feature of automatic data call at startup
2. Configure APN
'''
def cfgEnv(usrCfg):
    errcode = 0
    need_reboot1 = False
    need_reboot2 = False
    if "datacall_config.json" not in uos.listdir('/usr'):
        # Disable automatic activation at startup for the first cellular NIC
        dataCall.setAutoActivate(usrCfg['profileID'], 0)
        # It is recommended to enable the automatic reconnection for the cellular NIC
        dataCall.setAutoConnect(usrCfg['profileID'], 1)
        need_reboot1 = True

    print('Check the APN configuration.')
    # Get the APN information of the cellular NICs and check if the current one is the one you specified
    pdpCtx = dataCall.getPDPContext(usrCfg['profileID'])
    if pdpCtx != -1:
        if pdpCtx[1] != usrCfg['apn']:
            # If it is not the APN you need, configure it as follows
            ret = dataCall.setPDPContext(usrCfg['profileID'], 0, usrCfg['apn'], usrCfg['username'], usrCfg['password'], 0)
            if ret == 0:
                print('APN configuration successful.')
                need_reboot2 = True
            else:
                print('APN configuration failed.')
                errcode = -1
        else:
            print('The APN is correct and no configuration is required')
            errcode = 0
    else:
        print('Failed to get PDP Context.')
        errcode = -1
    # Reboot the module to make the configuration take effect
    if need_reboot1 or need_reboot2:
        print('Ready to restart.')
        print('Please re-execute this program after restarting.')
        Power.powerRestart()
        utime.sleep(2)
    return errcode


def main():
    if cfgEnv(usrCfg1) == -1:
        return

    # Manually activate the cellular NIC
    print('Prepare to activate the NIC{}.'.format(usrCfg1['profileID']))
    ret = dataCall.activate(usrCfg1['profileID'])
    if ret == -1:
        print('NIC activation failed.')
        return

    stage, state = checkNet.waitNetworkReady(10)
    if stage == 3 and state == 1:
        print('Network connected successfully.')
        # Get the IP address and other information of the first NIC
        ret = dataCall.getInfo(usrCfg1['profileID'], 0)
        print('NIC{}：{}'.format(usrCfg1['profileID'], ret))

        print('---------------sock test-----------------')
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

        # Decide whether to deactivate the NIC after communication ends as needed
        # dataCall.deactivate(usrCfg1['profileID'])
    else:
        print('Network connected failed, stage={}, state={}'.format(stage, state))


if __name__ == '__main__':
    main()
