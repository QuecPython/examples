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

nic = None

def eth_init():
    print('eth init start')
    nic = ethernet.CH395(b'\x12\x34\x56\x78\x9a\xbc','','','',-1,-1,-1,-1)
    nic_info = nic.ipconfig()
    print('nic net config before: {}'.format(nic_info))
    # dhcp ip config
    nic.dhcp()
    # static ip config 
    nic.set_addr('192.168.1.99', '255.255.255.0','192.168.1.1')
    nic.set_dns('8.8.8.8', '114.114.114.114')
    nic_info = nic.ipconfig()
    print('nic net config after: {}'.format(nic_info))
    nic.set_default_NIC(nic_info[1][1])
    nic.set_up()
    print('eth startup success')

eth_init()

# now, you can connect server by ethernet interface





    


