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
usrCfg2 = {'profileID': 2, 'apn': '3gwap', 'username': '', 'password': ''}

'''
Disable the feature of automatic data call at startup
The return value indicates whether the module needs rebooting
True - Need
False - Not need
'''
def disableAutoActivate():
    need_reboot = False
    if "datacall_config.json" not in uos.listdir('/usr'):
        # Disable automatic activation at startup for NIC1
        dataCall.setAutoActivate(1, 0)
        # It is recommended to enable the automatic reconnection for the cellular NICs
        dataCall.setAutoConnect(1, 1)
        need_reboot = True
    return need_reboot

'''
Configure APN parameters for the cellular NIC
The return value indicates whether the module needs rebooting
True - Need
False - Not need
'''
def cfgAPN(usrCfg):
    need_reboot = False
    print('Check the APN configuration of the NIC{}.'.format(usrCfg['profileID']))
    # Get the APN information of the cellular NICs and check if the current one is the one you specified
    pdpCtx = dataCall.getPDPContext(usrCfg['profileID'])
    if pdpCtx != -1:
        if pdpCtx[1] != usrCfg['apn']:
            # If it is not the APN you need, configure it as follows
            ret = dataCall.setPDPContext(usrCfg['profileID'], 0, usrCfg['apn'], usrCfg['username'], usrCfg['password'], 0)
            if ret == 0:
                print('APN configuration successful.')
                need_reboot = True
            else:
                raise ValueError("APN configuration failed.")
        else:
            need_reboot = False
            print('The APN is correct and no configuration is required')
    else:
        raise ValueError("Failed to get PDP Context.")
    return need_reboot


def main():
    need_reboot1 = disableAutoActivate()
    need_reboot2 = cfgAPN(usrCfg1)
    need_reboot3 = cfgAPN(usrCfg2)
    if need_reboot1 or need_reboot2 or need_reboot3:
        print('Ready to restart.')
        print('Please re-execute this program after restarting.')
        Power.powerRestart()
        utime.sleep(2)

    # Manually activate the cellular NICs
    print('Prepare to activate the NIC{}.'.format(usrCfg1['profileID']))
    ret = dataCall.activate(usrCfg1['profileID'])
    if ret == -1:
        print('NIC activation failed.')
        return
    print('Prepare to activate the NIC{}.'.format(usrCfg2['profileID']))
    ret = dataCall.activate(usrCfg2['profileID'])
    if ret == -1:
        print('NIC activation failed.')
        return

    stage, state = checkNet.waitNetworkReady(10)
    if stage == 3 and state == 1:
        print('Network connected successfully.')
        # Get the IP address of NIC2 and NIC2
        ret1 = dataCall.getInfo(usrCfg1['profileID'], 0)
        ret2 = dataCall.getInfo(usrCfg2['profileID'], 0)
        print('NIC{}：{}'.format(usrCfg1['profileID'], ret1))
        print('NIC{}：{}'.format(usrCfg2['profileID'], ret2))
        ip_nic1 = None
        ip_nic2 = None
        if ret1 == -1 or ret1[2][2] == '0.0.0.0':
            print("Error: Failed to get the IP of the NIC{}.".format(usrCfg1['profileID']))
            return
        else:
            ip_nic1 = ret1[2][2]
        if ret2 == -1 or ret2[2][2] == '0.0.0.0':
            print("Error: Failed to get the IP of the NIC{}.".format(usrCfg2['profileID']))
            return
        else:
            ip_nic2 = ret2[2][2]
        print('NIC{} IP：{}'.format(usrCfg1['profileID'], ip_nic1))
        print('NIC{} ip：{}'.format(usrCfg2['profileID'], ip_nic2))

        print('---------------sock1 test-----------------')
        # Create a socket object
        sock1 = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        # Resolve the domain name
        try:
            sockaddr = usocket.getaddrinfo('python.quectel.com', 80)[0][-1]
        except Exception:
            print('Domain name resolution failed.')
            sock1.close()
            return
        # Connect to the server
        sock1.connect(sockaddr)
        # Send data to the server
        ret = sock1.send('GET /News HTTP/1.1\r\nHost: python.quectel.com\r\nAccept-Encoding: deflate\r\nConnection: keep-alive\r\n\r\n')
        print('send {} bytes'.format(ret))
        # Receive data from the server
        data = sock1.recv(256)
        print('recv {} bytes:'.format(len(data)))
        print(data.decode())
        # Close the connection
        sock1.close()
        print('---------------sock2 test-----------------')
        sock2 = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.TCP_CUSTOMIZE_PORT)
        sock2.bind((ip_nic2, 0))
        sock2.settimeout(10)
        # Configure server IP address and port number. The IP address and port number below are for example only
        server_addr = ('220.180.239.212', 8305)
        # Connect to the server
        sock2.connect(server_addr)
        # Send data to the server
        ret = sock2.send('test data.')
        print('send {} bytes'.format(ret))
        # Receive data from the server
        try:
            data = sock2.recv(256)
            print('recv {} bytes:'.format(len(data)))
            print(data.decode())
        except Exception:
            print('No reply from server.')
        # Close the connection
        sock2.close()

        # ecide whether to deactivate the NIC after communication ends as needed
        # dataCall.deactivate(usrCfg1['profileID'])
        # dataCall.deactivate(usrCfg2['profileID'])
    else:
        print('Network connected failed, stage={}, state={}'.format(stage, state))


if __name__ == '__main__':
    main()
