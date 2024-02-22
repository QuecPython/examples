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


# 用户需要配置的APN信息，根据实际情况修改
usrCfg1 = {'profileID': 1, 'apn': '3gnet', 'username': '', 'password': ''}
usrCfg2 = {'profileID': 2, 'apn': '3gwap', 'username': '', 'password': ''}


def checkAPN(usrCfg, reboot=False):
    if type(usrCfg) != dict:
        print("Error: Input is not a dictionary.")
        return False

    print('Check the APN configuration of the {} network card.'.format(usrCfg['profileID']))
    # 获取网卡的APN信息，确认当前使用的是否是用户指定的APN
    pdpCtx = dataCall.getPDPContext(usrCfg['profileID'])
    if pdpCtx != -1:
        if pdpCtx[1] != usrCfg['apn']:
            # 如果不是用户需要的APN，使用如下方式配置
            ret = dataCall.setPDPContext(usrCfg['profileID'], 0, usrCfg['apn'], usrCfg['username'], usrCfg['password'], 0)
            if ret == 0:
                print('APN configuration successful.')
                # 重启后按照配置的信息进行拨号
                if reboot:
                    print('Ready to restart to make APN take effect.')
                    print('Please re-execute this program after restarting.')
                    Power.powerRestart()
                else:
                    return True
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
    # 使能第一路网卡开机自动激活功能
    dataCall.setAutoActivate(1, 1)
    # 使能第一路网卡自动重连功能
    dataCall.setAutoConnect(1, 1)
    # 使能第二路网卡开机自动激活功能
    dataCall.setAutoActivate(2, 1)
    # 使能第二路网卡自动重连功能
    dataCall.setAutoConnect(2, 1)

    # 检查第一路网卡的APN配置，暂时不重启
    checkpass = checkAPN(usrCfg1, reboot=False)
    if not checkpass:
        return
    # 检查第二路网卡的APN配置，配置后重启
    checkpass = checkAPN(usrCfg2, reboot=True)
    if not checkpass:
        return

    stage, state = checkNet.waitNetworkReady(20)
    if stage == 3 and state == 1:
        print('Network connected successfully.')
        # 分别获取第一路和第二路网卡的IP地址信息
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
        # 创建socket对象
        sock1 = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        # 解析域名
        try:
            sockaddr = usocket.getaddrinfo('python.quectel.com', 80)[0][-1]
        except Exception:
            print('Domain name resolution failed.')
            sock1.close()
            return
        # 建立连接
        sock1.connect(sockaddr)
        # 向服务端发送消息
        ret = sock1.send('GET /News HTTP/1.1\r\nHost: python.quectel.com\r\nAccept-Encoding: deflate\r\nConnection: keep-alive\r\n\r\n')
        print('send {} bytes'.format(ret))
        # 接收服务端消息
        data = sock1.recv(256)
        print('recv {} bytes:'.format(len(data)))
        print(data.decode())
        # 关闭连接
        sock1.close()
        print('---------------sock2 test-----------------')
        sock2 = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.TCP_CUSTOMIZE_PORT)
        sock2.bind((ip_nic2, 0))
        sock2.settimeout(10)
        # 服务器IP和端口，下面的IP和端口仅作示例参考
        server_addr = ('220.180.239.212', 8305)
        # 建立连接
        sock2.connect(server_addr)
        # 向服务器发送消息
        ret = sock2.send('test data.')
        print('send {} bytes'.format(ret))
        # 接收服务端消息
        try:
            data = sock2.recv(256)
            print('recv {} bytes:'.format(len(data)))
            print(data.decode())
        except Exception:
            print('No reply from server.')
        # 关闭连接
        sock2.close()
    else:
        print('Network connected failed, stage={}, state={}'.format(stage, state))


if __name__ == '__main__':
    main()
