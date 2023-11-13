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

from usr.WLAN import ESP8266
from machine import UART
import usocket

# Create a Wi-Fi NIC
wifi = ESP8266(UART.UART2, ESP8266.STA)
print('Wi-Fi nic created.')

# Configure the SSID and password, and connect to the router
ssid = 'ssid'
password = 'password'
wifi.station(ssid,password)
print('Wi-Fi connected: %s, %s.' % (ssid, password))

# Configure the DNS server address for the Wi-Fi NIC
wifi.set_dns('8.8.8.8', '114.114.114.114')
print('Wi-Fi DNS server configured.')

# Check the network configuration information
ip_conf = wifi.ipconfig()
print('get ip_conf:', ip_conf)

def tcp_client(address, port):
    # Create a socket object
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)
    print('socket object created.')
	
    # Before connecting to the server, bind the Wi-Fi NIC IP address
    local_address = ip_conf[0]
    sock.bind((local_address, 0))
    print('bind ethernet address: %s', local_address)
	
    # Resolve the domain name
    sockaddr=usocket.getaddrinfo(address, port)[0][-1]
    print('DNS for %s: %s' % (address, sockaddr[0]))
    
    # Connect to the TCP server
    sock.connect(sockaddr)
    print('tcp link established.')
    
    # More code in TCP client samples above