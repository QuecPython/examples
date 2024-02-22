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


def main():
    stage, state = checkNet.waitNetworkReady(20)
    if stage == 3 and state == 1:
        print('Network connected successfully.')
        # 创建一个socket对象
        sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        # 解析域名
        try:
            sockaddr = usocket.getaddrinfo('python.quectel.com', 80)[0][-1]
        except Exception:
            print('Domain name resolution failed.')
            sock.close()
            return
        # 建立连接
        sock.connect(sockaddr)
        # 向服务端发送消息
        ret = sock.send('GET /News HTTP/1.1\r\nHost: python.quectel.com\r\nAccept-Encoding: deflate\r\nConnection: keep-alive\r\n\r\n')
        print('send {} bytes'.format(ret))

        # 接收服务端消息
        data = sock.recv(256)
        print('recv {} bytes:'.format(len(data)))
        print(data.decode())

        # 关闭连接
        sock.close()
    else:
        print('Network connected failed, stage={}, state={}'.format(stage, state))


if __name__ == '__main__':
    main()
