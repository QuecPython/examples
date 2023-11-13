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

# Create an Ethernet NIC
eth = ethernet.W5500(b'\x12\x34\x56\x78\x9a\xbc','','','',-1,38,36,37, 0)
print('W5500 ethernet nic created.')

# Enable DHCP
eth.dhcp()
print('DHCP enabled.')

# After the NIC is registered, check the network configuration information
ip_conf = eth.ipconfig()
print('get ip_conf:', ip_conf)

# Set the Ethernet NIC as the default NIC
eth.set_default_NIC(ip_conf[1][1])
print('W5500 is set as default nic.')

# Enable the NIC
eth.set_up()
print('Ethernet nic enabled.')